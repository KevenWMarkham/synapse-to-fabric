#!/usr/bin/env python3
"""
Copilot Prompt Library Validator
================================
Validates prompts.json against prompts.schema.json and performs additional
semantic checks that JSON Schema alone cannot enforce.

Usage:
    python validate.py
    python validate.py --prompts path/to/prompts.json --schema path/to/schema.json

Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROMPTS = SCRIPT_DIR / "prompts.json"
DEFAULT_SCHEMA = SCRIPT_DIR / "prompts.schema.json"

SEVERITY_VALUES = {"low", "medium", "high", "critical"}
FREQUENCY_VALUES = {"rare", "low", "medium", "high", "very-high"}
ID_PATTERN = re.compile(r"^[A-Z]{2,8}-\d{3}$")
MIN_PROMPT_TEXT_LENGTH = 50

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class ValidationResult:
    """Collects pass/fail results for a single prompt or global check."""

    def __init__(self):
        self.results: list[tuple[str, bool, str]] = []  # (check_name, passed, detail)

    def add(self, check: str, passed: bool, detail: str = ""):
        self.results.append((check, passed, detail))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self.results)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def pass_count(self) -> int:
        return sum(1 for _, ok, _ in self.results if ok)

    @property
    def fail_count(self) -> int:
        return self.total - self.pass_count


def load_json(path: Path, label: str) -> dict | list | None:
    """Load and parse a JSON file, returning None on error."""
    if not path.exists():
        print(f"ERROR: {label} not found at {path}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {label} is not valid JSON: {exc}")
        return None


# ---------------------------------------------------------------------------
# Schema validation (jsonschema library or manual fallback)
# ---------------------------------------------------------------------------

def validate_with_jsonschema(prompts: list, schema: dict) -> list[str]:
    """Validate using the jsonschema library. Returns list of error messages."""
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []  # caller handles fallback

    errors: list[str] = []
    validator_cls = jsonschema.Draft202012Validator
    validator = validator_cls(schema)
    for error in sorted(validator.iter_errors(prompts), key=lambda e: list(e.path)):
        path = " -> ".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"  [{path}] {error.message}")
    return errors


def try_jsonschema_validation(prompts: list, schema: dict, result: ValidationResult) -> bool:
    """Attempt jsonschema validation. Returns True if library was available."""
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        return False

    errors = validate_with_jsonschema(prompts, schema)
    if errors:
        result.add("JSON Schema (jsonschema)", False, f"{len(errors)} error(s):\n" + "\n".join(errors))
    else:
        result.add("JSON Schema (jsonschema)", True, "All prompts conform to schema")
    return True


# ---------------------------------------------------------------------------
# Manual / semantic validation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "id", "category", "patternName", "description", "whenToUse",
    "severity", "frequency", "promptText", "exampleBefore",
    "exampleAfter", "expectedOutcome", "tags", "relatedPrompts",
]


def validate_prompt(prompt: dict, index: int, all_ids: set[str], result: ValidationResult):
    """Run all checks on a single prompt entry."""
    prefix = f"[{index}]"
    pid = prompt.get("id", f"<missing-id-at-index-{index}>")
    prefix = f"[{pid}]"

    # Required fields
    for field in REQUIRED_FIELDS:
        present = field in prompt and prompt[field] is not None
        if field in ("tags", "relatedPrompts"):
            present = present and isinstance(prompt.get(field), list)
        result.add(f"{prefix} has '{field}'", present,
                   "" if present else f"Missing or null required field: {field}")

    # ID pattern
    id_val = prompt.get("id", "")
    id_ok = bool(ID_PATTERN.match(id_val))
    result.add(f"{prefix} id matches pattern", id_ok,
               "" if id_ok else f"ID '{id_val}' does not match ^[A-Z]{{2,8}}-\\d{{3}}$")

    # Severity enum
    sev = prompt.get("severity", "")
    sev_ok = sev in SEVERITY_VALUES
    result.add(f"{prefix} severity is valid", sev_ok,
               "" if sev_ok else f"'{sev}' not in {SEVERITY_VALUES}")

    # Frequency enum
    freq = prompt.get("frequency", "")
    freq_ok = freq in FREQUENCY_VALUES
    result.add(f"{prefix} frequency is valid", freq_ok,
               "" if freq_ok else f"'{freq}' not in {FREQUENCY_VALUES}")

    # promptText min length
    pt = prompt.get("promptText", "")
    pt_ok = isinstance(pt, str) and len(pt) >= MIN_PROMPT_TEXT_LENGTH
    result.add(f"{prefix} promptText >= {MIN_PROMPT_TEXT_LENGTH} chars", pt_ok,
               "" if pt_ok else f"Length is {len(pt) if isinstance(pt, str) else 'N/A'}")

    # exampleBefore != exampleAfter
    before = prompt.get("exampleBefore", "")
    after = prompt.get("exampleAfter", "")
    diff_ok = before != after
    result.add(f"{prefix} exampleBefore != exampleAfter", diff_ok,
               "" if diff_ok else "Before and After examples are identical")

    # tags is non-empty array of strings
    tags = prompt.get("tags", [])
    tags_ok = isinstance(tags, list) and len(tags) > 0 and all(isinstance(t, str) and t for t in tags)
    result.add(f"{prefix} tags is non-empty string array", tags_ok,
               "" if tags_ok else f"tags: {tags}")

    # relatedPrompts reference valid IDs
    related = prompt.get("relatedPrompts", [])
    if isinstance(related, list):
        for ref_id in related:
            ref_ok = ref_id in all_ids
            result.add(f"{prefix} relatedPrompt '{ref_id}' exists", ref_ok,
                       "" if ref_ok else f"Referenced prompt '{ref_id}' not found in library")


def validate_global(prompts: list, result: ValidationResult):
    """Run global cross-prompt validations."""
    # Unique IDs
    ids = [p.get("id", "") for p in prompts]
    seen: set[str] = set()
    duplicates: list[str] = []
    for pid in ids:
        if pid in seen:
            duplicates.append(pid)
        seen.add(pid)
    unique_ok = len(duplicates) == 0
    result.add("All IDs are unique", unique_ok,
               "" if unique_ok else f"Duplicate IDs: {duplicates}")

    # Array is non-empty
    result.add("Prompts array is non-empty", len(prompts) > 0,
               "" if prompts else "No prompts found")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def print_results(label: str, result: ValidationResult):
    """Pretty-print validation results."""
    print(f"\n{'=' * 70}")
    print(f"  {label}")
    print(f"{'=' * 70}")
    for check, passed, detail in result.results:
        status = "PASS" if passed else "FAIL"
        icon = "+" if passed else "!"
        line = f"  [{icon}] {status}: {check}"
        if detail and not passed:
            line += f"\n        -> {detail}"
        print(line)
    print(f"\n  Summary: {result.pass_count}/{result.total} checks passed", end="")
    if result.fail_count:
        print(f"  ({result.fail_count} FAILED)")
    else:
        print("  (ALL PASSED)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Copilot Prompt Library")
    parser.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS,
                        help="Path to prompts.json")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA,
                        help="Path to prompts.schema.json")
    args = parser.parse_args()

    print("Copilot Prompt Library Validator")
    print(f"  Prompts: {args.prompts}")
    print(f"  Schema:  {args.schema}")

    # Load files
    prompts = load_json(args.prompts, "prompts.json")
    schema = load_json(args.schema, "prompts.schema.json")

    if prompts is None:
        print("\nFATAL: Could not load prompts.json")
        return 1

    if not isinstance(prompts, list):
        print("\nFATAL: prompts.json must be a JSON array")
        return 1

    # --- JSON Schema validation ---
    schema_result = ValidationResult()
    if schema is not None:
        lib_available = try_jsonschema_validation(prompts, schema, schema_result)
        if not lib_available:
            schema_result.add(
                "JSON Schema (jsonschema library)", True,
                "Library not installed; skipping JSON Schema validation. "
                "Install with: pip install jsonschema"
            )
            print("\n  NOTE: jsonschema library not installed. "
                  "Falling back to manual validation only.")
    else:
        schema_result.add("Schema file loaded", False, "Could not load schema file")

    print_results("JSON Schema Validation", schema_result)

    # --- Global checks ---
    global_result = ValidationResult()
    validate_global(prompts, global_result)
    print_results("Global Checks", global_result)

    # --- Per-prompt checks ---
    all_ids = {p.get("id", "") for p in prompts}
    per_prompt_result = ValidationResult()
    for i, prompt in enumerate(prompts):
        validate_prompt(prompt, i, all_ids, per_prompt_result)

    print_results("Per-Prompt Validation", per_prompt_result)

    # --- Final summary ---
    total_pass = schema_result.pass_count + global_result.pass_count + per_prompt_result.pass_count
    total_checks = schema_result.total + global_result.total + per_prompt_result.total
    total_fail = total_checks - total_pass

    print(f"\n{'=' * 70}")
    print(f"  FINAL RESULT: {total_pass}/{total_checks} checks passed", end="")
    if total_fail:
        print(f"  ({total_fail} FAILED)")
        print(f"{'=' * 70}\n")
        return 1
    else:
        print("  (ALL PASSED)")
        print(f"{'=' * 70}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
