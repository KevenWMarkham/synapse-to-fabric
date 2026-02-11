"""Batch plan report generation (JSON + Markdown)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .models import BatchPlan, Batch, DatabaseObject


class BatchPlanReporter:
    """Generates formatted reports from a BatchPlan in JSON and Markdown formats.

    The JSON report contains the full machine-readable plan suitable for
    downstream tooling. The Markdown report provides a human-readable
    migration plan document with executive summary, sprint timeline,
    per-batch details, and dependency analysis.
    """

    def to_json(self, plan: BatchPlan, output_path: str) -> None:
        """Write the BatchPlan as formatted JSON.

        Output includes metadata, per-batch details with full object lists,
        dependency graph summary, and any warnings.

        Args:
            plan: The BatchPlan to serialize.
            output_path: File path to write the JSON output to.
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        data = plan.to_dict()

        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def to_markdown(self, plan: BatchPlan, output_path: str) -> None:
        """Write a comprehensive Markdown migration plan report.

        Report sections:
        1. Header with engagement name and timestamp
        2. Executive summary: total objects, batches, sprints, pass rate
        3. Sprint timeline table
        4. Per-batch detail sections with object lists and dependencies
        5. Dependency graph summary
        6. Warnings section
        7. Migration order checklist

        Args:
            plan: The BatchPlan to report on.
            output_path: File path to write the Markdown output to.
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []

        # -- 1. Header --
        title = plan.engagement_name if plan.engagement_name else "Migration Batch Plan"
        lines.append(f"# {title}")
        lines.append("")
        lines.append(f"**Generated:** {plan.created_at}")
        lines.append(f"**Tool:** Fabric Migration Batch Planner")
        lines.append("")
        lines.append("---")
        lines.append("")

        # -- 2. Executive Summary --
        lines.append("## Executive Summary")
        lines.append("")

        passed = sum(b.passed_count for b in plan.batches)
        failed = sum(b.failed_count for b in plan.batches)
        pass_rate = (
            f"{passed / plan.total_objects * 100:.1f}%"
            if plan.total_objects > 0
            else "N/A"
        )

        lines.append(f"| Metric | Value |")
        lines.append(f"|---|---|")
        lines.append(f"| Total Objects | {plan.total_objects} |")
        lines.append(f"| Total Batches | {plan.total_batches} |")
        lines.append(f"| Total Sprints | {plan.total_sprints} |")
        lines.append(f"| Passed Objects | {passed} |")
        lines.append(f"| Failed Objects | {failed} |")
        lines.append(f"| Pass Rate | {pass_rate} |")
        lines.append("")

        if plan.warnings:
            lines.append(f"> **{len(plan.warnings)} warning(s)** detected. See Warnings section below.")
            lines.append("")

        lines.append("---")
        lines.append("")

        # -- 3. Sprint Timeline --
        lines.append("## Sprint Timeline")
        lines.append("")
        lines.append("| Sprint | Batch | Type Group | Objects | Passed | Failed | Depends On |")
        lines.append("|---|---|---|---|---|---|---|")

        for batch in plan.batches:
            dep_str = (
                ", ".join(str(d) for d in batch.dependencies) if batch.dependencies else "None"
            )
            lines.append(
                f"| {batch.sprint_number} | {batch.batch_name} | "
                f"{batch.object_type_group} | {batch.total_objects} | "
                f"{batch.passed_count} | {batch.failed_count} | "
                f"Batch {dep_str} |"
            )

        lines.append("")
        lines.append("---")
        lines.append("")

        # -- 4. Per-Batch Detail Sections --
        lines.append("## Batch Details")
        lines.append("")

        for batch in plan.batches:
            lines.append(f"### {batch.batch_name} (Sprint {batch.sprint_number})")
            lines.append("")
            lines.append(f"**Type Group:** {batch.object_type_group}")
            lines.append(f"**Objects:** {batch.total_objects} ({batch.passed_count} passed, {batch.failed_count} failed)")
            if batch.dependencies:
                dep_names = []
                for dep_id in batch.dependencies:
                    for other in plan.batches:
                        if other.batch_id == dep_id:
                            dep_names.append(f"{other.batch_name} (batch {dep_id})")
                            break
                lines.append(f"**Depends On:** {', '.join(dep_names)}")
            else:
                lines.append(f"**Depends On:** None (independent)")
            lines.append("")

            # Object list table
            if batch.objects:
                lines.append("| # | Object Name | Type | Schema | Status | Failure Reason |")
                lines.append("|---|---|---|---|---|---|")
                for idx, obj in enumerate(batch.objects, 1):
                    reason = obj.failure_reason if obj.failure_reason else "-"
                    # Truncate long failure reasons for readability
                    if len(reason) > 60:
                        reason = reason[:57] + "..."
                    lines.append(
                        f"| {idx} | `{obj.name}` | {obj.object_type.value} | "
                        f"{obj.schema_name} | {obj.status} | {reason} |"
                    )
                lines.append("")

            # Notes for failed objects
            failed_objs = [o for o in batch.objects if not o.passed]
            if failed_objs:
                lines.append(f"**Failed Objects ({len(failed_objs)}):**")
                lines.append("")
                for obj in failed_objs:
                    cat_str = f" [{obj.failure_category}]" if obj.failure_category else ""
                    lines.append(f"- `{obj.qualified_name}`{cat_str}: {obj.failure_reason}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # -- 5. Dependency Graph Summary --
        lines.append("## Dependency Analysis")
        lines.append("")

        dep_summary = plan.dependency_summary
        if dep_summary:
            lines.append(f"| Metric | Value |")
            lines.append(f"|---|---|")
            lines.append(f"| Total Nodes | {dep_summary.get('total_nodes', 0)} |")
            lines.append(f"| Total Edges | {dep_summary.get('total_edges', 0)} |")
            lines.append(f"| Dependency Layers | {dep_summary.get('num_layers', 0)} |")
            lines.append(f"| Max Chain Depth | {dep_summary.get('max_chain_depth', 0)} |")
            lines.append(f"| Circular Dependencies | {dep_summary.get('cycle_count', 0)} |")
            lines.append(f"| Root Nodes (no deps) | {dep_summary.get('root_nodes', 0)} |")
            lines.append(f"| Leaf Nodes (no dependents) | {dep_summary.get('leaf_nodes', 0)} |")
            lines.append("")

            cycles = dep_summary.get("cycles", [])
            if cycles:
                lines.append("### Circular Dependencies")
                lines.append("")
                for i, cycle in enumerate(cycles, 1):
                    lines.append(f"{i}. {' -> '.join(cycle)}")
                lines.append("")
        else:
            lines.append("No dependency analysis data available.")
            lines.append("")

        lines.append("---")
        lines.append("")

        # -- 6. Warnings --
        if plan.warnings:
            lines.append("## Warnings")
            lines.append("")
            for i, warning in enumerate(plan.warnings, 1):
                lines.append(f"{i}. {warning}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # -- 7. Migration Order Checklist --
        lines.append("## Migration Order Checklist")
        lines.append("")
        lines.append("Execute batches in the following order. Each batch should be fully")
        lines.append("migrated and validated before proceeding to the next.")
        lines.append("")

        for batch in plan.batches:
            lines.append(
                f"- [ ] **Sprint {batch.sprint_number} - {batch.batch_name}** "
                f"({batch.total_objects} objects)"
            )
            for obj in batch.objects:
                status_mark = "x" if obj.passed else " "
                lines.append(f"  - [{status_mark}] `{obj.qualified_name}` ({obj.object_type.value})")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by the Fabric Migration Batch Planner. "
                      "Review and adjust batch assignments before sprint execution.*")
        lines.append("")

        with open(output, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
