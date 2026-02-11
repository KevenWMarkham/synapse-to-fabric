"""Multi-format report generation."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .parser import AssessmentObject

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates assessment reports in JSON, HTML, and Markdown formats.

    Aggregates assessment results, dependency analysis, and triage data
    into structured reports suitable for stakeholder review and
    downstream processing by the batch grouping tool.
    """

    def __init__(
        self,
        objects: list[AssessmentObject],
        dependency_summary: dict[str, Any],
        triage_summary: dict[str, Any],
        migration_order: list[list[str]],
        copilot_suggestions: dict[str, list[str]],
        primary_failures: list[AssessmentObject],
        dependent_failures: list[AssessmentObject],
        source_file: str = "",
    ) -> None:
        """Initialize the report generator with all analysis results.

        Args:
            objects: Full list of assessed objects.
            dependency_summary: Summary dict from DependencyAnalyzer.summary().
            triage_summary: Summary dict from FailureTriage.get_summary().
            migration_order: Layered ordering from DependencyAnalyzer.
            copilot_suggestions: Prompt suggestions from FailureTriage.
            primary_failures: Root-cause failure objects.
            dependent_failures: Cascade failure objects.
            source_file: Path to the original input file.
        """
        self.objects = objects
        self.dependency_summary = dependency_summary
        self.triage_summary = triage_summary
        self.migration_order = migration_order
        self.copilot_suggestions = copilot_suggestions
        self.primary_failures = primary_failures
        self.dependent_failures = dependent_failures
        self.source_file = source_file
        self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _build_metadata(self) -> dict[str, Any]:
        """Build the report metadata section.

        Returns:
            Dictionary with timestamp, source file, and object counts.
        """
        total = len(self.objects)
        passed = sum(1 for o in self.objects if o.is_passed)
        failed = sum(1 for o in self.objects if o.is_failed)
        warning = sum(1 for o in self.objects if o.is_warning)
        pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0

        return {
            "generated_at": self.timestamp,
            "source_file": self.source_file,
            "tool": "Fabric Migration Assessment Processor",
            "version": "1.0.0",
            "total_objects": total,
            "passed_count": passed,
            "failed_count": failed,
            "warning_count": warning,
            "pass_rate": pass_rate,
        }

    def _build_object_inventory(self) -> dict[str, list[dict[str, Any]]]:
        """Group objects by type for the inventory section.

        Returns:
            Dictionary mapping object type to list of object dicts.
        """
        inventory: dict[str, list[dict[str, Any]]] = {}
        for obj in self.objects:
            obj_type = obj.object_type
            if obj_type not in inventory:
                inventory[obj_type] = []
            inventory[obj_type].append(obj.to_dict())

        # Sort each group by qualified name
        for obj_type in inventory:
            inventory[obj_type].sort(key=lambda o: o["qualified_name"])

        return inventory

    def _build_full_report_data(self) -> dict[str, Any]:
        """Assemble the complete report data structure.

        Returns:
            Full report dictionary used by all output formats.
        """
        metadata = self._build_metadata()
        inventory = self._build_object_inventory()

        # Build recommended actions sorted by impact and category
        actions = self._build_recommended_actions()

        return {
            "metadata": metadata,
            "objects": [o.to_dict() for o in self.objects],
            "object_inventory": inventory,
            "dependency_analysis": self.dependency_summary,
            "triage_summary": self.triage_summary,
            "primary_failures": [o.to_dict() for o in self.primary_failures],
            "dependent_failures": [o.to_dict() for o in self.dependent_failures],
            "migration_order": self.migration_order,
            "copilot_suggestions": self.copilot_suggestions,
            "recommended_actions": actions,
        }

    def _build_recommended_actions(self) -> list[dict[str, Any]]:
        """Build an ordered list of recommended remediation actions.

        Actions are prioritized by:
        1. Impact score (descending) -- fix high-impact items first
        2. Category (auto_fixable first, then minor_manual, then significant)

        Returns:
            List of action dicts with object info, category, and suggestions.
        """
        category_priority = {
            "auto_fixable": 0,
            "minor_manual": 1,
            "significant_refactor": 2,
            "uncategorized": 3,
        }

        failed_objects = [o for o in self.objects if o.is_failed]
        failed_objects.sort(
            key=lambda o: (
                category_priority.get(o.failure_category, 99),
                -o.impact_score,
            )
        )

        actions: list[dict[str, Any]] = []
        for idx, obj in enumerate(failed_objects, start=1):
            action: dict[str, Any] = {
                "priority": idx,
                "qualified_name": obj.qualified_name,
                "object_type": obj.object_type,
                "failure_reason": obj.failure_reason,
                "failure_category": obj.failure_category,
                "impact_score": obj.impact_score,
                "is_primary_failure": obj in self.primary_failures,
            }

            # Add Copilot prompt suggestions if available
            prompts = self.copilot_suggestions.get(obj.qualified_name, [])
            if prompts:
                action["suggested_prompts"] = prompts

            actions.append(action)

        return actions

    def generate_json(self, output_path: str) -> None:
        """Write the full report as structured JSON.

        Args:
            output_path: Path to write the JSON file.
        """
        report_data = self._build_full_report_data()

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info("JSON report written to: %s", output_path)

    def generate_html(
        self, output_path: str, template_path: str
    ) -> None:
        """Render the HTML report using a Jinja2 template.

        Args:
            output_path: Path to write the HTML file.
            template_path: Path to the Jinja2 HTML template file.
        """
        report_data = self._build_full_report_data()

        template_dir = str(Path(template_path).parent)
        template_name = Path(template_path).name

        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(["html"]),
        )

        # Add custom filters
        env.filters["status_color"] = _status_color_filter
        env.filters["category_color"] = _category_color_filter
        env.filters["category_label"] = _category_label_filter

        template = env.get_template(template_name)
        html_content = template.render(**report_data)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info("HTML report written to: %s", output_path)

    def generate_markdown(self, output_path: str) -> None:
        """Write the report in Markdown format.

        Args:
            output_path: Path to write the Markdown file.
        """
        report_data = self._build_full_report_data()
        meta = report_data["metadata"]
        triage = report_data["triage_summary"]
        dep = report_data["dependency_analysis"]

        lines: list[str] = []

        # Title
        lines.append("# Fabric Migration Assessment Report")
        lines.append("")
        lines.append(f"**Generated:** {meta['generated_at']}")
        lines.append(f"**Source:** {meta['source_file']}")
        lines.append(f"**Tool:** {meta['tool']} v{meta['version']}")
        lines.append("")

        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Total Objects | {meta['total_objects']} |")
        lines.append(f"| Passed | {meta['passed_count']} |")
        lines.append(f"| Failed | {meta['failed_count']} |")
        lines.append(f"| Warnings | {meta['warning_count']} |")
        lines.append(f"| Pass Rate | {meta['pass_rate']}% |")
        lines.append("")

        # Object Inventory
        lines.append("## Object Inventory")
        lines.append("")
        lines.append("| Type | Total | Passed | Failed | Warning |")
        lines.append("|------|-------|--------|--------|---------|")

        inventory = report_data["object_inventory"]
        for obj_type in sorted(inventory.keys()):
            type_objects = inventory[obj_type]
            total = len(type_objects)
            passed = sum(1 for o in type_objects if o["status"] == "PASSED")
            failed = sum(1 for o in type_objects if o["status"] == "FAILED")
            warning = sum(1 for o in type_objects if o["status"] == "WARNING")
            lines.append(
                f"| {obj_type} | {total} | {passed} | {failed} | {warning} |"
            )
        lines.append("")

        # Failure Analysis
        lines.append("## Failure Analysis")
        lines.append("")
        lines.append(f"### Primary Failures (Root Causes): {dep.get('primary_failures_count', 0)}")
        lines.append("")

        if report_data["primary_failures"]:
            lines.append("| Object | Type | Failure Reason | Impact Score |")
            lines.append("|--------|------|----------------|--------------|")
            for obj_dict in report_data["primary_failures"]:
                reason = obj_dict["failure_reason"][:80]
                lines.append(
                    f"| {obj_dict['qualified_name']} | {obj_dict['object_type']} "
                    f"| {reason} | {obj_dict['impact_score']} |"
                )
            lines.append("")

        lines.append(f"### Dependent Failures (Cascading): {dep.get('dependent_failures_count', 0)}")
        lines.append("")

        if report_data["dependent_failures"]:
            lines.append("| Object | Type | Failure Reason | Impact Score |")
            lines.append("|--------|------|----------------|--------------|")
            for obj_dict in report_data["dependent_failures"]:
                reason = obj_dict["failure_reason"][:80]
                lines.append(
                    f"| {obj_dict['qualified_name']} | {obj_dict['object_type']} "
                    f"| {reason} | {obj_dict['impact_score']} |"
                )
            lines.append("")

        # Dependency Summary
        lines.append("### Dependency Graph Summary")
        lines.append("")
        lines.append(f"- Total nodes: {dep.get('total_nodes', 0)}")
        lines.append(f"- Total edges: {dep.get('total_edges', 0)}")
        lines.append(f"- Max chain depth: {dep.get('max_chain_depth', 0)}")
        lines.append("")

        if dep.get("most_impactful_failures"):
            lines.append("**Top 5 Most Impactful Failures:**")
            lines.append("")
            for item in dep["most_impactful_failures"]:
                lines.append(
                    f"1. **{item['qualified_name']}** "
                    f"(impact: {item['impact_score']}) - "
                    f"{item['failure_reason'][:60]}"
                )
            lines.append("")

        # Triage Breakdown
        lines.append("## Triage Breakdown")
        lines.append("")
        lines.append(f"Total failures: {triage['total_failures']}")
        lines.append("")
        lines.append("| Category | Count | Percentage | Description |")
        lines.append("|----------|-------|------------|-------------|")

        for category in ["auto_fixable", "minor_manual", "significant_refactor", "uncategorized"]:
            count = triage["counts"].get(category, 0)
            pct = triage["percentages"].get(category, 0.0)
            desc = triage["descriptions"].get(category, "")
            label = _category_label_filter(category)
            lines.append(f"| {label} | {count} | {pct}% | {desc} |")
        lines.append("")

        if triage.get("uncategorized_reasons"):
            lines.append("### Uncategorized Failure Reasons (for review)")
            lines.append("")
            for reason in triage["uncategorized_reasons"]:
                lines.append(f"- {reason}")
            lines.append("")

        # Dependency Chains for top failures
        top_failures = dep.get("most_impactful_failures", [])
        if top_failures:
            lines.append("## Dependency Chains")
            lines.append("")
            lines.append("Dependency chains for the most impactful failures:")
            lines.append("")
            for item in top_failures[:3]:
                lines.append(f"### {item['qualified_name']}")
                lines.append("")
                # Find matching object for chains
                matching = [
                    o for o in self.objects
                    if o.qualified_name == item["qualified_name"]
                ]
                if matching:
                    from .dependency_analyzer import DependencyAnalyzer
                    # Build chains from the stored data if available
                    lines.append(f"Impact score: {item['impact_score']} downstream objects blocked")
                    lines.append("")
                lines.append("")

        # Recommended Actions
        lines.append("## Recommended Actions")
        lines.append("")

        actions = report_data["recommended_actions"]
        if actions:
            for action in actions[:20]:
                primary_marker = " [ROOT CAUSE]" if action["is_primary_failure"] else ""
                prompts_text = ""
                if action.get("suggested_prompts"):
                    prompts_text = f" (Copilot prompts: {', '.join(action['suggested_prompts'])})"

                lines.append(
                    f"{action['priority']}. **{action['qualified_name']}** "
                    f"({action['object_type']}) - "
                    f"[{_category_label_filter(action['failure_category'])}]{primary_marker}\n"
                    f"   - {action['failure_reason']}{prompts_text}"
                )
                lines.append("")

        # Migration Order
        lines.append("## Migration Order")
        lines.append("")
        lines.append(
            "Objects grouped into layers for safe migration ordering "
            "(all objects in a layer can be migrated in parallel):"
        )
        lines.append("")

        for layer_idx, layer in enumerate(report_data["migration_order"]):
            lines.append(f"### Layer {layer_idx + 1} ({len(layer)} objects)")
            lines.append("")
            for obj_name in layer:
                lines.append(f"- {obj_name}")
            lines.append("")

        # Copilot Suggestions
        if report_data["copilot_suggestions"]:
            lines.append("## Copilot Prompt Suggestions")
            lines.append("")
            for obj_name, prompts in sorted(
                report_data["copilot_suggestions"].items()
            ):
                lines.append(f"- **{obj_name}**: {', '.join(prompts)}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(
            f"*Generated by {meta['tool']} v{meta['version']} "
            f"on {meta['generated_at']}*"
        )
        lines.append("")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info("Markdown report written to: %s", output_path)

    def generate_all(
        self,
        output_dir: str,
        formats: list[str],
        template_path: str | None = None,
    ) -> list[str]:
        """Generate reports in all requested formats.

        Args:
            output_dir: Directory to write report files.
            formats: List of format strings: "json", "html", "markdown".
            template_path: Path to the Jinja2 HTML template (required if
                "html" is in formats).

        Returns:
            List of paths to generated report files.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp_slug = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        generated_files: list[str] = []

        for fmt in formats:
            fmt_lower = fmt.lower().strip()

            if fmt_lower == "json":
                path = os.path.join(
                    output_dir, f"assessment_report_{timestamp_slug}.json"
                )
                self.generate_json(path)
                generated_files.append(path)

            elif fmt_lower == "html":
                path = os.path.join(
                    output_dir, f"assessment_report_{timestamp_slug}.html"
                )
                if template_path and os.path.exists(template_path):
                    self.generate_html(path, template_path)
                else:
                    logger.warning(
                        "HTML template not found at '%s'. "
                        "Skipping HTML report generation.",
                        template_path,
                    )
                    continue
                generated_files.append(path)

            elif fmt_lower in ("markdown", "md"):
                path = os.path.join(
                    output_dir, f"assessment_report_{timestamp_slug}.md"
                )
                self.generate_markdown(path)
                generated_files.append(path)

            else:
                logger.warning("Unknown report format: '%s', skipping.", fmt)

        logger.info(
            "Generated %d report(s) in %s.",
            len(generated_files),
            output_dir,
        )
        return generated_files


def _status_color_filter(status: str) -> str:
    """Jinja2 filter: map status to CSS color.

    Args:
        status: Object status string.

    Returns:
        CSS color string.
    """
    colors = {
        "PASSED": "#28a745",
        "FAILED": "#dc3545",
        "WARNING": "#ffc107",
    }
    return colors.get(status.upper(), "#6c757d")


def _category_color_filter(category: str) -> str:
    """Jinja2 filter: map triage category to CSS color.

    Args:
        category: Triage category name.

    Returns:
        CSS color string.
    """
    colors = {
        "auto_fixable": "#86BC25",
        "minor_manual": "#ffc107",
        "significant_refactor": "#dc3545",
        "uncategorized": "#6c757d",
    }
    return colors.get(category, "#6c757d")


def _category_label_filter(category: str) -> str:
    """Jinja2 filter: map category key to human-readable label.

    Args:
        category: Category key string.

    Returns:
        Human-readable label.
    """
    labels = {
        "auto_fixable": "Auto-Fixable",
        "minor_manual": "Minor Manual",
        "significant_refactor": "Significant Refactor",
        "uncategorized": "Uncategorized",
    }
    return labels.get(category, category.replace("_", " ").title())
