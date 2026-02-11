# Assessment Processor

Process and analyze Fabric Migration Assistant assessment output to identify root-cause failures, categorize fix effort, map dependency chains, and generate multi-format reports.

## Features

- **Multi-format input**: Accepts CSV and JSON assessment exports with configurable column mappings
- **Dependency analysis**: Builds a directed graph of object dependencies using NetworkX, identifies primary (root cause) vs. dependent (cascade) failures, and calculates impact scores
- **Failure triage**: Categorizes each failure as auto-fixable, minor manual, or significant refactor using configurable regex patterns
- **Copilot prompt mapping**: Maps failure patterns to relevant prompt IDs from the E0-S3 Copilot prompt library
- **Migration ordering**: Computes a layered topological sort for safe migration sequencing
- **Multi-format reports**: Generates JSON (machine-readable), HTML (stakeholder-ready), and Markdown reports

## Prerequisites

- Python 3.10 or later
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# Run with the included sample CSV
python process_assessment.py examples/sample_assessment.csv

# Run with JSON input and custom output directory
python process_assessment.py examples/sample_assessment.json --output-dir ./my-reports

# Verbose mode with specific report formats
python process_assessment.py data/export.csv --verbose --report-formats json,markdown

# Use a custom config file
python process_assessment.py export.csv --config my_config.yaml
```

## Input Formats

### CSV

The CSV parser uses configurable column mappings. Default expected columns:

| Column | Description | Required |
|--------|-------------|----------|
| `ObjectName` | Name of the database object | Yes |
| `ObjectType` | Type: TABLE, VIEW, STORED_PROCEDURE, FUNCTION, etc. | Yes |
| `SchemaName` | Schema name (defaults to `dbo` if missing) | Yes |
| `MigrationStatus` | Assessment result: Passed, Failed, or Warning | Yes |
| `FailureReason` | Description of why the object failed | No |
| `Dependencies` | Semicolon-delimited list of dependent object names | No |

Column names are case-insensitive and can be remapped in `config.yaml`.

### JSON

Expects a JSON array (or an object with an `"objects"` key containing an array). Each element must have:

```json
{
  "name": "DimCustomer",
  "object_type": "TABLE",
  "schema_name": "dbo",
  "status": "Passed",
  "failure_reason": "",
  "dependencies": ["dbo.DimProduct"]
}
```

## Configuration

Copy `config.template.yaml` to `config.yaml` and customize:

```bash
cp config.template.yaml config.yaml
```

### Key configuration sections

**input.column_mappings** -- Map your CSV export columns to the expected logical names if they differ from defaults.

**analysis.categories** -- Define failure triage categories with regex patterns. The processor tries each category in order and assigns the first match. Categories:
- `auto_fixable`: Copilot or scripts can fix automatically
- `minor_manual`: Less than 1 hour manual effort per object
- `significant_refactor`: More than 1 hour manual effort per object

**analysis.dependency** -- Control dependency graph behavior:
- `enable_impact_scoring`: Calculate how many downstream objects each failure blocks
- `max_depth`: Maximum traversal depth for dependency chains

**output** -- Report generation settings:
- `directory`: Where to write reports
- `report_formats`: Which formats to generate (json, html, markdown)
- `html_template`: Path to the Jinja2 HTML template

## Output Formats

### JSON

Machine-readable structured report containing all analysis data: metadata, full object list, dependency analysis summary, triage breakdown, migration order, and recommended actions. Suitable for downstream tool consumption (e.g., batch grouping tool).

### HTML

Stakeholder-ready visual report with:
- Executive summary cards (total/passed/failed/warning/pass rate)
- Object inventory grouped by type with status indicators
- Failure analysis with primary vs. dependent breakdown
- Triage breakdown with colored progress bars
- Impact-ranked recommended actions with Copilot prompt links
- Layered migration order visualization

### Markdown

Text-based report suitable for inclusion in wikis, pull requests, or documentation. Contains all analysis sections in GitHub-compatible Markdown.

## Integration

The Assessment Processor fits into the Fabric Migration Assistant pipeline:

```
DACPAC Extract  -->  Assessment Processor  -->  Batch Grouping Tool
   (dacpac-extract)     (this tool)              (batch-grouping)
```

- **Receives**: DACPAC assessment CSV/JSON output from the Fabric Migration Assistant portal or SqlPackage CLI
- **Produces**: Structured reports consumed by the batch grouping tool for sprint-level migration planning
- **References**: Copilot prompt IDs from the `copilot-prompts` library for automated fix suggestions

## Example Workflow

```bash
# 1. Extract DACPAC and run migration assessment (produces assessment_export.csv)
#    (done via Fabric portal or SqlPackage CLI)

# 2. Configure the processor for your engagement
cp config.template.yaml config.yaml
# Edit config.yaml to map your column names and adjust patterns

# 3. Process the assessment
python process_assessment.py assessment_export.csv --output-dir ./reports --verbose

# 4. Review the HTML report
#    Open ./reports/assessment_report_<timestamp>.html in a browser

# 5. Feed JSON report into batch grouping tool
#    The JSON output is structured for direct consumption by the
#    batch grouping tool for sprint planning
```

## CLI Reference

```
usage: process_assessment.py [-h] [--output-dir OUTPUT_DIR] [--config CONFIG]
                              [--format {csv,json,auto}]
                              [--report-formats REPORT_FORMATS] [--verbose]
                              input_file

positional arguments:
  input_file            Path to the assessment input file (CSV or JSON)

options:
  -h, --help            Show help message and exit
  --output-dir DIR      Output directory for reports (default: from config)
  --config PATH         Config YAML file path (default: ./config.yaml)
  --format {csv,json,auto}
                        Force input format (default: auto-detect)
  --report-formats FMT  Comma-separated: json,html,markdown (default: all)
  --verbose             Enable verbose/debug output
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success -- all objects passed assessment |
| 1 | Success -- failures found (reports generated) |
| 2 | Error -- processing failed (file not found, invalid input, etc.) |
