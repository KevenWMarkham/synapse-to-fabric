# Copilot Prompt Library

Pre-built library of **12 Copilot prompts** for automating common Synapse-to-Fabric migration code fixes. Each prompt is designed to be copy-pasted into GitHub Copilot Chat, Azure Data Studio Copilot, or any LLM-powered coding assistant alongside the SQL code that needs transformation.

## Purpose

During Synapse-to-Fabric migrations, hundreds or thousands of SQL objects (tables, views, stored procedures, scripts) require syntax changes to become compatible with Microsoft Fabric Warehouse. These changes follow repeatable patterns -- distribution hints, index declarations, identity columns, external tables, and more.

This library provides **structured, validated Copilot prompts** that encode the migration rules for each pattern. Instead of writing ad-hoc instructions for each fix, migration engineers select the appropriate prompt from the catalog, paste it into their Copilot assistant alongside the SQL code, and receive a correctly transformed result.

The prompts are organized by category and severity, cross-referenced with related patterns, and include before/after examples for validation.

## Files

| File | Description |
|------|-------------|
| `prompts.json` | Array of 12 structured prompt entries with metadata, instructions, and examples |
| `prompts.schema.json` | JSON Schema for validating the structure of `prompts.json` |
| `validate.py` | Validation script that checks `prompts.json` against the schema and performs semantic checks |
| `render_catalog.py` | Generates `catalog.md` from `prompts.json` with summary statistics and formatted documentation |
| `catalog.md` | Human-readable reference catalog of all prompts (auto-generated) |
| `README.md` | This file |

## Prompt Coverage

| ID | Pattern | Category | Severity | Frequency |
|----|---------|----------|----------|-----------|
| DIST-001 | Distribution Hint Removal | DDL Compatibility | High | Very High |
| CCI-001 | Clustered Columnstore Index Removal | Index Management | Medium | High |
| IDENT-001 | IDENTITY Column Conversion | DDL Compatibility | High | High |
| MATVIEW-001 | Materialized View Conversion | View Conversion | High | Medium |
| EXTBL-001 | External Table Conversion | External Data | Critical | High |
| CTAS-001 | CTAS Statement Conversion | DDL Compatibility | Medium | High |
| WLM-001 | Workload Management Removal | Resource Management | Low | Medium |
| XDBREF-001 | Cross-Database Reference Resolution | Query Compatibility | Critical | Medium |
| UNICODE-001 | Unicode String Normalization | Data Type | Medium | Low |
| DTYPE-001 | Deprecated Data Type Replacement | Data Type | Medium | Medium |
| PART-001 | Partition Scheme Conversion | DDL Compatibility | High | Low |
| STATS-001 | Statistics Creation Syntax Update | Performance | Low | High |

## Usage

### Validating prompts.json

Run the validator to ensure all prompts conform to the schema and pass semantic checks:

```bash
python validate.py
```

The validator performs the following checks:

- **JSON Schema validation** (requires `jsonschema` library; falls back to manual checks if unavailable)
- **Unique IDs** across all prompts
- **ID pattern matching** (e.g., `DIST-001`)
- **Required fields** present on every prompt
- **Severity and frequency** values match allowed enums
- **promptText minimum length** (50 characters)
- **exampleBefore differs from exampleAfter** for every prompt
- **relatedPrompts reference valid IDs** that exist in the library

Install the optional jsonschema library for full schema validation:

```bash
pip install jsonschema
```

Custom file paths:

```bash
python validate.py --prompts /path/to/prompts.json --schema /path/to/schema.json
```

Exit code is `0` on success, `1` on any failure.

### Rendering the catalog

Regenerate `catalog.md` after updating `prompts.json`:

```bash
python render_catalog.py
```

Custom file paths:

```bash
python render_catalog.py --prompts /path/to/prompts.json --output /path/to/catalog.md
```

### Using prompts in Copilot

1. **Identify the pattern** -- Use the assessment processor output or `catalog.md` to find which prompt applies to your SQL code.

2. **Open Copilot Chat** -- In VS Code, Azure Data Studio, or your IDE with Copilot enabled, open the chat panel.

3. **Paste the prompt** -- Copy the `promptText` from `catalog.md` (in the code block under "Copilot Prompt") or directly from `prompts.json`.

4. **Paste the SQL code** -- Below the prompt, paste the SQL code that needs transformation.

5. **Review the output** -- Verify the Copilot response matches the expected pattern shown in the before/after examples.

6. **Batch processing** -- For bulk migrations, integrate the prompts programmatically:

   ```python
   import json

   with open("prompts.json") as f:
       prompts = json.load(f)

   # Find prompt by ID
   prompt = next(p for p in prompts if p["id"] == "DIST-001")

   # Construct the full Copilot message
   message = f"{prompt['promptText']}\n\n```sql\n{your_sql_code}\n```"
   ```

## Adding New Prompts

1. **Choose an ID** -- Follow the pattern `PREFIX-NNN` where `PREFIX` is a 2-8 character uppercase code for the category and `NNN` is a zero-padded sequence number. Check existing IDs to avoid conflicts.

2. **Add the entry to `prompts.json`** -- Include all required fields as defined in `prompts.schema.json`:

   ```json
   {
     "id": "NEWPAT-001",
     "category": "Category Name",
     "patternName": "Human-Readable Pattern Name",
     "description": "Detailed description of what this prompt addresses...",
     "whenToUse": "Practical guidance on when to apply this prompt...",
     "severity": "low|medium|high|critical",
     "frequency": "rare|low|medium|high|very-high",
     "promptText": "The Copilot-ready prompt text (minimum 50 characters)...",
     "exampleBefore": "-- Original Synapse SQL\nCREATE TABLE ...",
     "exampleAfter": "-- Converted Fabric SQL\nCREATE TABLE ...",
     "expectedOutcome": "Description of expected result after applying the prompt...",
     "tags": ["tag1", "tag2", "tag3"],
     "relatedPrompts": ["DIST-001", "CCI-001"]
   }
   ```

3. **Validate** -- Run `python validate.py` and fix any reported issues.

4. **Regenerate catalog** -- Run `python render_catalog.py` to update `catalog.md`.

5. **Review** -- Open `catalog.md` to verify the new entry renders correctly with proper formatting.

## Integration with Assessment Processor

The assessment processor (`../assessment-processor/`) scans Synapse SQL codebases and produces findings categorized by pattern type. Each finding can be mapped to a Copilot prompt from this library:

| Assessment Finding | Prompt ID |
|--------------------|-----------|
| Distribution hint detected | DIST-001 |
| Explicit CCI declaration | CCI-001 |
| IDENTITY column found | IDENT-001 |
| Materialized view found | MATVIEW-001 |
| External table (PolyBase) | EXTBL-001 |
| CTAS with distribution | CTAS-001 |
| Workload management DDL | WLM-001 |
| Cross-database reference | XDBREF-001 |
| VARCHAR with Unicode data | UNICODE-001 |
| Deprecated data type | DTYPE-001 |
| Partition function/scheme | PART-001 |
| Statistics with options | STATS-001 |

The assessment processor output includes the finding type which can be used to look up the corresponding prompt ID programmatically:

```python
import json

with open("prompts.json") as f:
    prompts = {p["id"]: p for p in json.load(f)}

# Map assessment finding to prompt
finding_type = "DIST-001"  # from assessment processor output
if finding_type in prompts:
    prompt = prompts[finding_type]
    print(f"Apply prompt: {prompt['patternName']}")
    print(f"Instructions: {prompt['promptText']}")
```

## Requirements

- Python 3.10+ (for validate.py and render_catalog.py)
- Optional: `jsonschema` library for full JSON Schema validation (`pip install jsonschema`)
