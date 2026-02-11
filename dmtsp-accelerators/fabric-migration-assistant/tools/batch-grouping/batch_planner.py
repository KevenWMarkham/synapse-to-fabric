"""
Fabric Migration Batch Planner

Analyzes assessment output, builds dependency graphs, and creates
optimized migration batch plans with sprint assignments.

Usage:
    python batch_planner.py analyze --input assessment.json [options]

Commands:
    analyze     Create batch plan from assessment data
    validate    Validate an existing batch plan
    visualize   Generate dependency graph summary

Options:
    --input PATH       Assessment JSON input (from assessment processor)
    --config PATH      Config file (default: config.yaml)
    --output PATH      Output file (default: batch_plan.json)
    --format FMT       Output formats: json,markdown (default: both)
    --engagement NAME  Engagement name for reports
    --verbose          Verbose output
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from modules.models import BatchPlan, DatabaseObject
from modules.dependency_graph import DependencyGraph
from modules.balanced_strategy import BalancedBatchingStrategy
from modules.reporters import BatchPlanReporter


# ANSI color codes for console output
class _Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"


def _supports_color() -> bool:
    """Check if the terminal supports ANSI color codes."""
    if sys.platform == "win32":
        try:
            import os
            return os.environ.get("TERM") is not None or os.environ.get("WT_SESSION") is not None
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_USE_COLOR = _supports_color()


def _c(color: str, text: str) -> str:
    """Apply ANSI color to text if terminal supports it."""
    if _USE_COLOR:
        return f"{color}{text}{_Colors.RESET}"
    return text


def _load_config(config_path: str | None) -> dict:
    """Load configuration from YAML file or return defaults.

    Args:
        config_path: Path to config.yaml, or None to use defaults.

    Returns:
        Configuration dictionary.
    """
    default_config = {
        "batching": {
            "table_batch_count": 4,
            "view_batch_count": 2,
            "balance_tolerance": 20,
            "min_batch_size": 3,
        },
        "ordering": {
            "type_priority": [
                "SCHEMA", "SECURITY", "FUNCTION", "TABLE", "VIEW",
                "STORED_PROCEDURE", "STATISTICS", "EXTERNAL_TABLE",
                "EXTERNAL_DATA_SOURCE", "EXTERNAL_FILE_FORMAT",
            ],
            "sprint_mapping": {
                "foundation": 1,
                "table_batches": [2, 3, 4, 5],
                "view_batches": [6, 7],
                "procedures": 8,
                "cleanup": 9,
            },
        },
        "dependency": {
            "providers": [
                "foreign_key", "view_reference",
                "procedure_reference", "function_reference",
            ],
            "circular_resolution": "warn",
        },
    }

    if config_path is None:
        # Try default location
        default_location = Path(__file__).parent / "config.yaml"
        if default_location.exists():
            config_path = str(default_location)
        else:
            return default_config

    config_file = Path(config_path)
    if not config_file.exists():
        print(_c(_Colors.YELLOW, f"[WARN] Config file not found: {config_path}. Using defaults."))
        return default_config

    with open(config_file, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)

    if not isinstance(loaded, dict):
        print(_c(_Colors.YELLOW, f"[WARN] Config file is empty or invalid. Using defaults."))
        return default_config

    # Merge loaded config with defaults (loaded takes precedence)
    merged = default_config.copy()
    for key in loaded:
        if isinstance(loaded[key], dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **loaded[key]}
        else:
            merged[key] = loaded[key]

    return merged


def _print_header() -> None:
    """Print the tool header banner."""
    print()
    print(_c(_Colors.BOLD, "=" * 60))
    print(_c(_Colors.BOLD, "  Fabric Migration Batch Planner"))
    print(_c(_Colors.BOLD, "  DMTSP Accelerator — Batch Grouping Tool"))
    print(_c(_Colors.BOLD, "=" * 60))
    print()


def _print_summary(plan: BatchPlan) -> None:
    """Print a formatted console summary of the batch plan.

    Args:
        plan: The completed BatchPlan.
    """
    passed = sum(b.passed_count for b in plan.batches)
    failed = sum(b.failed_count for b in plan.batches)

    print(_c(_Colors.BOLD, "--- Plan Summary ---"))
    print(f"  Engagement:    {plan.engagement_name or '(not specified)'}")
    print(f"  Total Objects: {plan.total_objects}")
    print(f"  Passed:        {_c(_Colors.GREEN, str(passed))}")
    print(f"  Failed:        {_c(_Colors.RED, str(failed))}")
    print(f"  Total Batches: {plan.total_batches}")
    print(f"  Total Sprints: {plan.total_sprints}")
    print()

    print(_c(_Colors.BOLD, "--- Sprint Assignment ---"))
    for batch in plan.batches:
        status_color = _Colors.GREEN if batch.failed_count == 0 else _Colors.YELLOW
        dep_str = ""
        if batch.dependencies:
            dep_str = f" (depends on batch {', '.join(str(d) for d in batch.dependencies)})"
        print(
            f"  Sprint {batch.sprint_number}: "
            f"{_c(status_color, batch.batch_name)} — "
            f"{batch.total_objects} objects "
            f"({batch.passed_count}P / {batch.failed_count}F)"
            f"{dep_str}"
        )
    print()

    if plan.warnings:
        print(_c(_Colors.YELLOW, f"--- Warnings ({len(plan.warnings)}) ---"))
        for i, warning in enumerate(plan.warnings, 1):
            print(f"  {_c(_Colors.YELLOW, f'[{i}]')} {warning}")
        print()


def cmd_analyze(args: argparse.Namespace) -> int:
    """Execute the analyze command: create batch plan from assessment data.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code: 0 for success, 1 for warnings, 2 for errors.
    """
    _print_header()

    # Load input
    input_path = args.input
    if not Path(input_path).exists():
        print(_c(_Colors.RED, f"[ERROR] Assessment file not found: {input_path}"))
        return 2

    print(f"Loading assessment: {input_path}")
    try:
        objects = BatchPlan.from_assessment_json(input_path)
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(_c(_Colors.RED, f"[ERROR] Failed to parse assessment file: {e}"))
        return 2

    print(f"  Parsed {len(objects)} objects")

    # Load config
    config = _load_config(args.config)
    if args.verbose:
        print(f"  Config: {json.dumps(config.get('batching', {}), indent=2)}")

    # Build dependency graph
    print("Building dependency graph...")
    graph = DependencyGraph(objects)
    summary = graph.summary()
    print(f"  Nodes: {summary['total_nodes']}, Edges: {summary['total_edges']}, "
          f"Layers: {summary['num_layers']}, Cycles: {summary['cycle_count']}")

    # Create batch plan
    print("Creating batch plan...")
    strategy = BalancedBatchingStrategy(config)
    engagement_name = args.engagement or ""
    plan = strategy.create_plan(objects, graph, engagement_name=engagement_name)

    # Print summary
    _print_summary(plan)

    # Generate outputs
    output_formats = [f.strip().lower() for f in args.format.split(",")]
    output_base = args.output
    reporter = BatchPlanReporter()

    if "json" in output_formats:
        json_path = output_base if output_base.endswith(".json") else f"{output_base}.json"
        reporter.to_json(plan, json_path)
        print(_c(_Colors.GREEN, f"[OK] JSON plan written to: {json_path}"))

    if "markdown" in output_formats:
        md_path = output_base.replace(".json", "") + ".md"
        reporter.to_markdown(plan, md_path)
        print(_c(_Colors.GREEN, f"[OK] Markdown report written to: {md_path}"))

    print()

    if plan.warnings:
        return 1
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Execute the validate command: verify an existing batch plan.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code: 0 for valid, 1 for warnings, 2 for errors.
    """
    _print_header()

    input_path = args.input
    if not Path(input_path).exists():
        print(_c(_Colors.RED, f"[ERROR] Batch plan file not found: {input_path}"))
        return 2

    print(f"Validating batch plan: {input_path}")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(_c(_Colors.RED, f"[ERROR] Invalid JSON: {e}"))
        return 2

    issues: list[str] = []

    # Check required top-level keys
    if "metadata" not in data:
        issues.append("Missing 'metadata' section")
    if "batches" not in data:
        issues.append("Missing 'batches' section")
        print(_c(_Colors.RED, f"[ERROR] {issues[-1]}"))
        return 2

    metadata = data.get("metadata", {})
    batches = data.get("batches", [])

    # Validate metadata
    total_objects = metadata.get("total_objects", 0)
    actual_total = sum(b.get("total_objects", 0) for b in batches)
    if total_objects != actual_total:
        issues.append(
            f"Object count mismatch: metadata says {total_objects}, "
            f"batches contain {actual_total}"
        )

    # Validate batch dependencies
    batch_ids = {b.get("batch_id") for b in batches}
    for batch in batches:
        batch_name = batch.get("batch_name", "?")
        for dep_id in batch.get("dependencies", []):
            if dep_id not in batch_ids:
                issues.append(
                    f"Batch '{batch_name}' depends on batch {dep_id} "
                    f"which does not exist"
                )
            bid = batch.get("batch_id")
            if dep_id is not None and bid is not None and dep_id >= bid:
                issues.append(
                    f"Batch '{batch_name}' (id={bid}) depends on "
                    f"batch {dep_id} which has a later or equal id"
                )

    # Validate sprint ordering matches dependency ordering
    batch_id_to_sprint: dict[int, int] = {}
    for batch in batches:
        bid = batch.get("batch_id")
        sprint = batch.get("sprint_number")
        if bid is not None and sprint is not None:
            batch_id_to_sprint[bid] = sprint

    for batch in batches:
        bid = batch.get("batch_id")
        sprint = batch.get("sprint_number")
        for dep_id in batch.get("dependencies", []):
            dep_sprint = batch_id_to_sprint.get(dep_id)
            if dep_sprint is not None and sprint is not None and dep_sprint >= sprint:
                issues.append(
                    f"Sprint ordering issue: '{batch.get('batch_name')}' "
                    f"(sprint {sprint}) depends on batch {dep_id} "
                    f"(sprint {dep_sprint})"
                )

    # Validate no duplicate objects across batches
    seen_objects: dict[str, str] = {}
    for batch in batches:
        batch_name = batch.get("batch_name", "?")
        for obj in batch.get("objects", []):
            qname = obj.get("qualified_name", "")
            if qname in seen_objects:
                issues.append(
                    f"Duplicate object '{qname}' found in "
                    f"'{batch_name}' and '{seen_objects[qname]}'"
                )
            seen_objects[qname] = batch_name

    # Report results
    if issues:
        print(_c(_Colors.YELLOW, f"\n  Found {len(issues)} issue(s):"))
        for i, issue in enumerate(issues, 1):
            print(f"    {_c(_Colors.YELLOW, f'[{i}]')} {issue}")
        print()
        return 1
    else:
        print(_c(_Colors.GREEN, "\n  Batch plan is valid. No issues found."))
        print(f"    Batches: {len(batches)}")
        print(f"    Objects: {actual_total}")
        print(f"    Sprints: {len(set(batch_id_to_sprint.values()))}")
        print()
        return 0


def cmd_visualize(args: argparse.Namespace) -> int:
    """Execute the visualize command: generate text-based dependency visualization.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code: 0 for success, 2 for errors.
    """
    _print_header()

    input_path = args.input
    if not Path(input_path).exists():
        print(_c(_Colors.RED, f"[ERROR] Assessment file not found: {input_path}"))
        return 2

    print(f"Loading assessment: {input_path}")
    try:
        objects = BatchPlan.from_assessment_json(input_path)
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        print(_c(_Colors.RED, f"[ERROR] Failed to parse assessment file: {e}"))
        return 2

    print(f"  Parsed {len(objects)} objects")
    print()

    # Build graph
    graph = DependencyGraph(objects)
    summary = graph.summary()

    # Print summary
    print(_c(_Colors.BOLD, "--- Dependency Graph Summary ---"))
    print(f"  Total Nodes:   {summary['total_nodes']}")
    print(f"  Total Edges:   {summary['total_edges']}")
    print(f"  Layers:        {summary['num_layers']}")
    print(f"  Max Depth:     {summary['max_chain_depth']}")
    print(f"  Cycles:        {summary['cycle_count']}")
    print(f"  Root Nodes:    {summary['root_nodes']}")
    print(f"  Leaf Nodes:    {summary['leaf_nodes']}")
    print()

    # Print layer view
    layers = graph.get_layers()
    print(_c(_Colors.BOLD, "--- Dependency Layers ---"))
    print()

    # Build object type lookup for display
    obj_lookup = {obj.qualified_name: obj for obj in objects}

    for layer_idx, layer_nodes in enumerate(layers):
        indent = "  " * layer_idx
        connector = "|" if layer_idx > 0 else " "
        arrow = "+--> " if layer_idx > 0 else "     "

        print(f"  {_c(_Colors.CYAN, f'Layer {layer_idx}')} ({len(layer_nodes)} objects)")
        for node in layer_nodes:
            obj = obj_lookup.get(node)
            type_label = obj.object_type.value if obj else "?"
            status = ""
            if obj:
                if obj.passed:
                    status = _c(_Colors.GREEN, "[PASS]")
                else:
                    status = _c(_Colors.RED, "[FAIL]")

            # Show dependencies
            deps = graph.get_dependencies(node)
            dep_str = ""
            if deps:
                dep_names = sorted(deps)
                if len(dep_names) <= 3:
                    dep_str = f" <- {', '.join(dep_names)}"
                else:
                    dep_str = f" <- {', '.join(dep_names[:3])} +{len(dep_names) - 3} more"

            print(f"  {indent}{arrow}{node} ({type_label}) {status}{dep_str}")

        print()

    # Print cycles if any
    cycles = summary.get("cycles", [])
    if cycles:
        print(_c(_Colors.YELLOW, "--- Circular Dependencies ---"))
        for i, cycle in enumerate(cycles, 1):
            print(f"  {_c(_Colors.YELLOW, f'Cycle {i}:')} {' -> '.join(cycle)} -> {cycle[0]}")
        print()

    # Print key dependency chains (longest paths)
    print(_c(_Colors.BOLD, "--- Key Dependency Chains ---"))
    print()

    # Find objects with deepest ancestor chains
    chain_depths: list[tuple[str, int]] = []
    for obj in objects:
        ancestors = graph.get_ancestors(obj.qualified_name)
        chain_depths.append((obj.qualified_name, len(ancestors)))

    chain_depths.sort(key=lambda x: -x[1])

    for qname, depth in chain_depths[:5]:
        if depth == 0:
            continue
        ancestors = graph.get_ancestors(qname)
        # Find one path from a root ancestor to this node
        path = _trace_path(graph, qname)
        print(f"  {qname} (depth {depth})")
        print(f"    Chain: {' -> '.join(path)}")
        print()

    return 0


def _trace_path(graph: DependencyGraph, target: str) -> list[str]:
    """Trace one dependency path from a root ancestor to the target node.

    Uses a greedy approach: from the target, walk back to the dependency with
    the most ancestors, building the longest reasonable path.

    Args:
        graph: The dependency graph.
        target: Qualified name of the target node.

    Returns:
        List of qualified names from root to target.
    """
    path = [target]
    current = target
    visited: set[str] = {target}

    while True:
        deps = graph.get_dependencies(current)
        deps = deps - visited
        if not deps:
            break

        # Pick the dependency with the most ancestors (longest chain)
        best_dep = max(deps, key=lambda d: len(graph.get_ancestors(d)))
        path.append(best_dep)
        visited.add(best_dep)
        current = best_dep

    path.reverse()
    return path


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with subcommands.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="batch_planner",
        description="Fabric Migration Batch Planner — analyze assessment data and "
                    "create optimized migration batch plans with sprint assignments.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python batch_planner.py analyze --input assessment.json
  python batch_planner.py analyze --input assessment.json --config config.yaml --engagement "Contoso Migration"
  python batch_planner.py validate --input batch_plan.json
  python batch_planner.py visualize --input assessment.json --verbose
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # -- analyze --
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Create batch plan from assessment data",
    )
    analyze_parser.add_argument(
        "--input", required=True,
        help="Assessment JSON input file (from assessment processor E0-S2)",
    )
    analyze_parser.add_argument(
        "--config", default=None,
        help="Config file path (default: config.yaml in tool directory)",
    )
    analyze_parser.add_argument(
        "--output", default="batch_plan.json",
        help="Output file path (default: batch_plan.json)",
    )
    analyze_parser.add_argument(
        "--format", default="json,markdown",
        help="Output formats, comma-separated: json, markdown (default: both)",
    )
    analyze_parser.add_argument(
        "--engagement", default="",
        help="Engagement name for report headers",
    )
    analyze_parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose output",
    )

    # -- validate --
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate an existing batch plan",
    )
    validate_parser.add_argument(
        "--input", required=True,
        help="Batch plan JSON file to validate",
    )
    validate_parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose output",
    )

    # -- visualize --
    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Generate dependency graph summary",
    )
    visualize_parser.add_argument(
        "--input", required=True,
        help="Assessment JSON input file (from assessment processor)",
    )
    visualize_parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose output",
    )

    return parser


def main() -> int:
    """Main entry point for the batch planner CLI.

    Returns:
        Exit code: 0 success, 1 warnings, 2 errors.
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "analyze":
            return cmd_analyze(args)
        elif args.command == "validate":
            return cmd_validate(args)
        elif args.command == "visualize":
            return cmd_visualize(args)
        else:
            parser.print_help()
            return 0
    except Exception as e:
        print(_c(_Colors.RED, f"\n[ERROR] Unexpected error: {e}"))
        if hasattr(args, "verbose") and args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
