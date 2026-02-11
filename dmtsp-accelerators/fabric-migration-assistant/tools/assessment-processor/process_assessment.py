"""
Fabric Migration Assessment Processor

Analyzes migration assessment output from Fabric Migration Assistant,
identifies primary vs dependent failures, categorizes fix effort,
and generates multi-format reports.

Usage:
    python process_assessment.py <input_file> [options]

Options:
    --output-dir DIR      Output directory (default: ./output)
    --config PATH         Config file path (default: ./config.yaml)
    --format FORMAT       Force input format: csv|json (default: auto-detect)
    --report-formats FMT  Comma-separated: json,html,markdown (default: all)
    --verbose             Enable verbose output
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

import yaml

from modules.parser import AssessmentParser
from modules.dependency_analyzer import DependencyAnalyzer
from modules.triage import FailureTriage
from modules.report_generator import ReportGenerator

# ANSI color codes for console output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "dim": "\033[2m",
}


def colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color codes.

    Falls back to plain text if stdout is not a terminal.

    Args:
        text: The text to colorize.
        color: Color key from COLORS dict.

    Returns:
        Colorized string (or plain string if not a TTY).
    """
    if not sys.stdout.isatty():
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def load_config(config_path: str) -> dict[str, Any]:
    """Load configuration from a YAML file with sensible defaults.

    If the config file does not exist, returns a default configuration
    that matches config.template.yaml.

    Args:
        config_path: Path to the YAML config file.

    Returns:
        Configuration dictionary.
    """
    defaults: dict[str, Any] = {
        "input": {
            "default_format": "csv",
            "column_mappings": {
                "object_name": "ObjectName",
                "object_type": "ObjectType",
                "schema_name": "SchemaName",
                "status": "MigrationStatus",
                "failure_reason": "FailureReason",
                "dependencies": "Dependencies",
            },
        },
        "analysis": {
            "categories": {
                "auto_fixable": {
                    "description": "Can be automatically fixed by Copilot prompts or scripts",
                    "patterns": [
                        "DISTRIBUTION.*not supported",
                        "CLUSTERED COLUMNSTORE.*default",
                        "IDENTITY.*not supported",
                        "STATISTICS.*syntax",
                        "CTAS.*distribution",
                    ],
                },
                "minor_manual": {
                    "description": "Requires minor manual intervention (< 1 hour per object)",
                    "patterns": [
                        "MATERIALIZED VIEW",
                        "WORKLOAD.*CLASSIFIER",
                        "deprecated.*data type",
                        "UNICODE.*collation",
                        "PARTITION.*scheme",
                    ],
                },
                "significant_refactor": {
                    "description": "Requires significant refactoring (> 1 hour per object)",
                    "patterns": [
                        "EXTERNAL TABLE.*DATA_SOURCE",
                        "cross.database.*reference",
                        "stored procedure.*incompatible",
                        "complex.*dependency",
                    ],
                },
            },
            "dependency": {
                "enable_impact_scoring": True,
                "max_depth": 10,
            },
        },
        "output": {
            "directory": "./output",
            "report_formats": ["json", "html", "markdown"],
            "html_template": "templates/report.html",
            "include_timestamp": True,
        },
    }

    if not os.path.exists(config_path):
        logging.info(
            "Config file '%s' not found. Using default configuration.",
            config_path,
        )
        return defaults

    with open(config_path, "r", encoding="utf-8") as f:
        user_config = yaml.safe_load(f) or {}

    # Deep merge user config over defaults
    merged = _deep_merge(defaults, user_config)
    return merged


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence.

    Args:
        base: Base dictionary (defaults).
        override: Override dictionary (user-provided values).

    Returns:
        Merged dictionary.
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def print_summary(
    objects: list,
    primary_failures: list,
    dependent_failures: list,
    triage_summary: dict[str, Any],
    dep_summary: dict[str, Any],
    copilot_suggestions: dict[str, list[str]],
) -> None:
    """Print a color-coded summary to the console.

    Args:
        objects: All assessment objects.
        primary_failures: Root-cause failures.
        dependent_failures: Cascade failures.
        triage_summary: Triage results summary.
        dep_summary: Dependency analysis summary.
        copilot_suggestions: Copilot prompt suggestions.
    """
    total = len(objects)
    passed = sum(1 for o in objects if o.is_passed)
    failed = sum(1 for o in objects if o.is_failed)
    warnings = sum(1 for o in objects if o.is_warning)
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0.0

    print()
    print(colorize("=" * 60, "cyan"))
    print(colorize("  FABRIC MIGRATION ASSESSMENT RESULTS", "bold"))
    print(colorize("=" * 60, "cyan"))
    print()

    # Object counts
    print(f"  Total objects assessed:  {colorize(str(total), 'bold')}")
    print(f"  {colorize('Passed', 'green')}:  {passed}")
    print(f"  {colorize('Failed', 'red')}:  {failed}")
    print(f"  {colorize('Warnings', 'yellow')}:  {warnings}")
    print(f"  Pass rate:  {colorize(f'{pass_rate}%', 'green' if pass_rate >= 80 else 'yellow' if pass_rate >= 50 else 'red')}")
    print()

    # Failure analysis
    print(colorize("  FAILURE ANALYSIS", "bold"))
    print(colorize("  " + "-" * 40, "dim"))
    print(f"  Primary failures (root causes):  {colorize(str(len(primary_failures)), 'red')}")
    print(f"  Dependent failures (cascading):   {colorize(str(len(dependent_failures)), 'yellow')}")
    print(f"  Max dependency chain depth:       {dep_summary.get('max_chain_depth', 0)}")
    print()

    # Triage breakdown
    print(colorize("  TRIAGE BREAKDOWN", "bold"))
    print(colorize("  " + "-" * 40, "dim"))
    counts = triage_summary.get("counts", {})
    pcts = triage_summary.get("percentages", {})

    auto_count = counts.get("auto_fixable", 0)
    minor_count = counts.get("minor_manual", 0)
    sig_count = counts.get("significant_refactor", 0)
    uncat_count = counts.get("uncategorized", 0)

    print(f"  {colorize('Auto-fixable', 'green')}:          {auto_count:3d}  ({pcts.get('auto_fixable', 0)}%)")
    print(f"  {colorize('Minor manual', 'yellow')}:         {minor_count:3d}  ({pcts.get('minor_manual', 0)}%)")
    print(f"  {colorize('Significant refactor', 'red')}:   {sig_count:3d}  ({pcts.get('significant_refactor', 0)}%)")
    print(f"  {colorize('Uncategorized', 'dim')}:          {uncat_count:3d}  ({pcts.get('uncategorized', 0)}%)")
    print()

    # Top impactful failures
    top_failures = dep_summary.get("most_impactful_failures", [])
    if top_failures:
        print(colorize("  TOP IMPACT FAILURES", "bold"))
        print(colorize("  " + "-" * 40, "dim"))
        for idx, item in enumerate(top_failures, start=1):
            name = item["qualified_name"]
            score = item["impact_score"]
            reason = item["failure_reason"][:50]
            print(f"  {idx}. {colorize(name, 'bold')} (impact: {score}) - {reason}")
        print()

    # Copilot suggestions count
    if copilot_suggestions:
        prompt_count = sum(len(v) for v in copilot_suggestions.values())
        print(
            f"  {colorize('Copilot prompt suggestions', 'cyan')}: "
            f"{prompt_count} prompts for {len(copilot_suggestions)} objects"
        )
        print()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed argument namespace.
    """
    parser = argparse.ArgumentParser(
        description="Fabric Migration Assessment Processor - "
        "Analyze migration assessment output, identify root-cause failures, "
        "categorize fix effort, and generate multi-format reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_assessment.py assessment_export.csv
  python process_assessment.py data.json --output-dir ./reports --verbose
  python process_assessment.py export.csv --config my_config.yaml --report-formats json,markdown
        """,
    )

    parser.add_argument(
        "input_file",
        help="Path to the assessment input file (CSV or JSON).",
    )

    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for reports (default: from config or ./output).",
    )

    parser.add_argument(
        "--config",
        default="./config.yaml",
        help="Path to config YAML file (default: ./config.yaml).",
    )

    parser.add_argument(
        "--format",
        choices=["csv", "json", "auto"],
        default="auto",
        help="Force input format (default: auto-detect from extension).",
    )

    parser.add_argument(
        "--report-formats",
        default=None,
        help="Comma-separated report formats: json,html,markdown (default: all from config).",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose/debug output.",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for the assessment processor.

    Returns:
        Exit code: 0 for success, 1 if failures found, 2 if processing error.
    """
    args = parse_arguments()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("assessment_processor")

    # Resolve paths relative to this script's directory
    script_dir = Path(__file__).parent.resolve()

    try:
        # Load configuration
        config_path = args.config
        if not os.path.isabs(config_path):
            config_path = str(script_dir / config_path)
        config = load_config(config_path)

        # Determine output directory
        output_dir = args.output_dir
        if output_dir is None:
            output_dir = config.get("output", {}).get("directory", "./output")
        if not os.path.isabs(output_dir):
            output_dir = str(script_dir / output_dir)

        # Determine report formats
        if args.report_formats:
            report_formats = [
                f.strip() for f in args.report_formats.split(",")
            ]
        else:
            report_formats = config.get("output", {}).get(
                "report_formats", ["json", "html", "markdown"]
            )

        # Resolve HTML template path
        html_template = config.get("output", {}).get(
            "html_template", "templates/report.html"
        )
        if not os.path.isabs(html_template):
            html_template = str(script_dir / html_template)

        # Resolve input file
        input_file = args.input_file
        if not os.path.isabs(input_file):
            input_file = str(Path.cwd() / input_file)

        logger.info("Input file: %s", input_file)
        logger.info("Output directory: %s", output_dir)
        logger.info("Report formats: %s", report_formats)

        # Step 1: Parse input
        print(colorize("\n[1/4] Parsing assessment input...", "cyan"))
        column_mappings = config.get("input", {}).get("column_mappings")
        parser = AssessmentParser(column_mappings=column_mappings)
        objects = parser.parse(input_file, format=args.format)
        print(f"      Parsed {colorize(str(len(objects)), 'bold')} objects.")

        if not objects:
            print(colorize("\nNo objects found in input file. Exiting.", "yellow"))
            return 2

        # Step 2: Dependency analysis
        print(colorize("\n[2/4] Analyzing dependencies...", "cyan"))
        dep_config = config.get("analysis", {}).get("dependency", {})
        max_depth = dep_config.get("max_depth", 10)
        enable_impact = dep_config.get("enable_impact_scoring", True)

        analyzer = DependencyAnalyzer(
            objects=objects,
            max_depth=max_depth,
            enable_impact_scoring=enable_impact,
        )

        primary_failures = analyzer.identify_primary_failures()
        dependent_failures = analyzer.identify_dependent_failures()
        dep_summary = analyzer.summary()
        migration_order = analyzer.get_migration_order()

        print(
            f"      Graph: {dep_summary['total_nodes']} nodes, "
            f"{dep_summary['total_edges']} edges."
        )
        print(
            f"      Primary failures: {colorize(str(len(primary_failures)), 'red')}, "
            f"Dependent: {colorize(str(len(dependent_failures)), 'yellow')}"
        )

        # Step 3: Triage categorization
        print(colorize("\n[3/4] Categorizing failures...", "cyan"))
        categories = config.get("analysis", {}).get("categories")
        triage = FailureTriage(categories=categories)
        objects = triage.categorize(objects)
        triage_summary = triage.get_summary()
        copilot_suggestions = triage.suggest_copilot_prompts(objects)

        auto_count = triage_summary["counts"].get("auto_fixable", 0)
        minor_count = triage_summary["counts"].get("minor_manual", 0)
        sig_count = triage_summary["counts"].get("significant_refactor", 0)
        print(
            f"      Auto-fixable: {colorize(str(auto_count), 'green')}, "
            f"Minor manual: {colorize(str(minor_count), 'yellow')}, "
            f"Significant: {colorize(str(sig_count), 'red')}"
        )

        # Step 4: Generate reports
        print(colorize("\n[4/4] Generating reports...", "cyan"))
        generator = ReportGenerator(
            objects=objects,
            dependency_summary=dep_summary,
            triage_summary=triage_summary,
            migration_order=migration_order,
            copilot_suggestions=copilot_suggestions,
            primary_failures=primary_failures,
            dependent_failures=dependent_failures,
            source_file=args.input_file,
        )

        generated_files = generator.generate_all(
            output_dir=output_dir,
            formats=report_formats,
            template_path=html_template,
        )

        for filepath in generated_files:
            print(f"      Written: {colorize(filepath, 'dim')}")

        # Print summary
        print_summary(
            objects=objects,
            primary_failures=primary_failures,
            dependent_failures=dependent_failures,
            triage_summary=triage_summary,
            dep_summary=dep_summary,
            copilot_suggestions=copilot_suggestions,
        )

        # Determine exit code
        failed_count = sum(1 for o in objects if o.is_failed)
        if failed_count > 0:
            print(
                colorize(
                    f"Assessment complete: {failed_count} failure(s) found. "
                    f"See reports in {output_dir}",
                    "yellow",
                )
            )
            return 1
        else:
            print(
                colorize(
                    "Assessment complete: All objects passed! "
                    f"Reports written to {output_dir}",
                    "green",
                )
            )
            return 0

    except FileNotFoundError as exc:
        logger.error("File not found: %s", exc)
        print(colorize(f"\nError: {exc}", "red"))
        return 2

    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        print(colorize(f"\nError: {exc}", "red"))
        return 2

    except Exception as exc:
        logger.exception("Unexpected error during processing.")
        print(colorize(f"\nUnexpected error: {exc}", "red"))
        return 2


if __name__ == "__main__":
    sys.exit(main())
