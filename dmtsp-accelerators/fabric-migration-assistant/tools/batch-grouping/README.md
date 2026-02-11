# Batch Grouping Tool

**Accelerator:** Fabric Migration Assistant (Acc 1)
**Phase:** E0-S2 — Discovery & Accelerator Setup
**Author:** DMTSP Team

## Purpose

The Batch Grouping Tool analyzes assessment processor output and creates optimized migration batch plans with sprint assignments. It consumes the JSON output from the Assessment Processor (E0-S2), builds a dependency graph, partitions objects into balanced batches respecting migration ordering constraints, and generates sprint-ready migration plans.

## Features

- **Dependency Analysis** — Builds a directed acyclic graph from declared and implicit dependencies. Detects circular dependencies with configurable resolution (warn, break, error).
- **Balanced Batching** — Partitions tables and views into configurable batch counts with round-robin assignment, dependency-aware ordering, and balance tolerance enforcement.
- **Sprint Assignment** — Maps batch type groups (foundation, table, view, procedure, cleanup) to sprint numbers via configuration.
- **Cycle Detection** — Uses Tarjan's algorithm to identify strongly connected components in the dependency graph.
- **Topological Sort** — Kahn's algorithm ensures objects are ordered so all dependencies are migrated first.
- **Layer Decomposition** — Groups objects into dependency layers for visualization and batch assignment.
- **Dual Report Output** — Generates both machine-readable JSON and human-readable Markdown reports.

## Prerequisites

- Python 3.10+
- PyYAML (`pip install pyyaml`)

No other external dependencies are required.

## Quick Start

```bash
# 1. Copy and customize configuration
cp config.template.yaml config.yaml

# 2. Run analysis on assessment output
python batch_planner.py analyze --input path/to/assessment.json --engagement "Contoso Migration"

# 3. Review output
#    - batch_plan.json   — Machine-readable batch plan
#    - batch_plan.md     — Human-readable migration report
```

### Try with sample data

```bash
python batch_planner.py analyze \
  --input examples/sample_assessment.json \
  --output examples/batch_plan.json \
  --engagement "Sample Engagement"
```

## Commands

### analyze

Create a batch plan from assessment data.

```bash
python batch_planner.py analyze --input assessment.json [options]
```

| Option | Default | Description |
|---|---|---|
| `--input PATH` | (required) | Assessment JSON from E0-S2 assessment processor |
| `--config PATH` | `config.yaml` | Configuration file |
| `--output PATH` | `batch_plan.json` | Output file path |
| `--format FMT` | `json,markdown` | Output formats (comma-separated) |
| `--engagement NAME` | (empty) | Engagement name for report headers |
| `--verbose` | false | Enable verbose console output |

### validate

Validate an existing batch plan for consistency.

```bash
python batch_planner.py validate --input batch_plan.json
```

Checks:
- Object count consistency between metadata and batch contents
- Batch dependency references point to valid batches
- Sprint ordering matches dependency ordering
- No duplicate objects across batches

### visualize

Generate a text-based dependency graph summary.

```bash
python batch_planner.py visualize --input assessment.json
```

Displays:
- Dependency graph statistics (nodes, edges, layers, cycles)
- Layer-by-layer object layout with status indicators
- Key dependency chains (longest paths)
- Circular dependency warnings

## Input Format

The tool consumes JSON output from the Assessment Processor (E0-S2). The expected structure:

```json
{
  "metadata": {
    "source_file": "synapse_assessment_export.csv",
    "processed_at": "2025-01-15T10:30:00Z",
    "total_objects": 20,
    "passed": 12,
    "failed": 8
  },
  "objects": [
    {
      "name": "Customers",
      "object_type": "TABLE",
      "schema_name": "dbo",
      "status": "Passed",
      "failure_reason": "",
      "dependencies": ["dbo.dbo"],
      "failure_category": "",
      "impact_score": 12
    }
  ],
  "dependency_analysis": {
    "impact_scores": { "dbo.Customers": 12 }
  }
}
```

### Supported Object Types

| Type | Description |
|---|---|
| `SCHEMA` | Database schemas |
| `SECURITY` | Roles, users, permissions |
| `FUNCTION` | Scalar and table-valued functions |
| `TABLE` | Regular tables |
| `VIEW` | Standard and materialized views |
| `STORED_PROCEDURE` | Stored procedures |
| `STATISTICS` | Column statistics |
| `EXTERNAL_TABLE` | External tables (PolyBase) |
| `EXTERNAL_DATA_SOURCE` | External data sources |
| `EXTERNAL_FILE_FORMAT` | External file formats |

## Configuration Reference

See `config.template.yaml` for the full configuration with comments. Key settings:

### Batching

| Setting | Default | Description |
|---|---|---|
| `table_batch_count` | 4 | Number of batches for tables |
| `view_batch_count` | 2 | Number of batches for views |
| `balance_tolerance` | 20 | Max % imbalance between batches |
| `min_batch_size` | 3 | Minimum objects per batch |

### Sprint Mapping

| Group | Default Sprint | Description |
|---|---|---|
| `foundation` | 1 | Schemas, security, functions |
| `table_batches` | [2, 3, 4, 5] | One sprint per table batch |
| `view_batches` | [6, 7] | One sprint per view batch |
| `procedures` | 8 | All stored procedures |
| `cleanup` | 9 | Statistics, external objects |

### Dependency

| Setting | Default | Description |
|---|---|---|
| `circular_resolution` | `warn` | How to handle cycles: `warn`, `break`, or `error` |

## Output Formats

### JSON Batch Plan

The JSON output contains:

- **metadata** — Engagement name, timestamp, totals, pass rate
- **batches** — Array of batch objects, each with:
  - Batch ID, name, sprint number, type group
  - Object list with full details (name, type, schema, status, failure reason)
  - Batch dependency list (which batches must complete first)
- **dependency_summary** — Graph statistics (nodes, edges, layers, cycles)
- **warnings** — Any issues detected during planning

### Markdown Report

The Markdown report provides:

- Executive summary with key metrics
- Sprint timeline table
- Per-batch detail sections with object lists
- Dependency graph analysis
- Warnings (if any)
- Migration order checklist with pass/fail indicators

## Batching Algorithm

The balanced batching strategy follows this sequence:

1. **Classify** — Separate objects into type groups: foundation (schemas, security, functions), tables, views, stored procedures, and cleanup (statistics, external objects).

2. **Foundation Batch** — All schemas, security objects, and functions go into batch 1 (sprint 1). These have no internal ordering constraints.

3. **Table Partitioning** — Tables are partitioned into N balanced batches:
   - Sort by dependency layer (layer 0 first)
   - Within each layer, sort by impact score descending
   - Round-robin to the smallest batch, respecting: if A depends on B, A goes in same or later batch
   - Rebalance if any batch exceeds the tolerance threshold

4. **View Partitioning** — Same algorithm as tables, into M batches. Each view batch depends on all table batches.

5. **Procedure Batch** — All stored procedures in one batch, depending on tables and views.

6. **Cleanup Batch** — Statistics and external objects last, depending on everything else.

7. **Validation** — Check no object in batch N depends on an object in batch N+1 or later.

## Integration

This tool sits between the Assessment Processor and sprint execution:

```
DACPAC Extract (E0-S1)
    |
    v
Assessment Processor (E0-S2) --> assessment.json
    |
    v
Batch Grouping Tool (E0-S2) --> batch_plan.json + batch_plan.md
    |
    v
Sprint Execution (Sprints 1-9)
```

**Receives:** Assessment JSON from the Assessment Processor
**Produces:** Sprint-ready migration batch plan consumed by the execution team

## Example Workflow

```bash
# Step 1: Run assessment processor on DACPAC export
python ../assessment-processor/assess.py --input synapse_export.csv --output assessment.json

# Step 2: Configure batch grouping for this engagement
cp config.template.yaml config.yaml
# Edit config.yaml: adjust batch counts, sprint mapping, tolerance

# Step 3: Generate batch plan
python batch_planner.py analyze \
  --input assessment.json \
  --config config.yaml \
  --output output/batch_plan.json \
  --engagement "Contoso Synapse-to-Fabric Migration" \
  --verbose

# Step 4: Validate the plan
python batch_planner.py validate --input output/batch_plan.json

# Step 5: Visualize dependencies
python batch_planner.py visualize --input assessment.json

# Step 6: Review output
#   output/batch_plan.json — Import into project tracking
#   output/batch_plan.md  — Share with stakeholders
```

## Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success — plan generated with no warnings |
| 1 | Warnings — plan generated but with dependency or balance warnings |
| 2 | Error — plan could not be generated (invalid input, unresolvable cycles) |
