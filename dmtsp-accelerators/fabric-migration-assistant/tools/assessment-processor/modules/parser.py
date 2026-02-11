"""Assessment input parser - supports CSV and JSON formats."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Canonical object type names for normalization
VALID_OBJECT_TYPES = {
    "TABLE",
    "VIEW",
    "STORED_PROCEDURE",
    "FUNCTION",
    "SCHEMA",
    "EXTERNAL_TABLE",
    "EXTERNAL_DATA_SOURCE",
    "EXTERNAL_FILE_FORMAT",
    "STATISTICS",
    "SECURITY",
    "INDEX",
    "CONSTRAINT",
    "TRIGGER",
    "SEQUENCE",
    "USER",
    "ROLE",
}

# Map common alternative type names to canonical names
TYPE_ALIASES: dict[str, str] = {
    "PROC": "STORED_PROCEDURE",
    "PROCEDURE": "STORED_PROCEDURE",
    "SP": "STORED_PROCEDURE",
    "SPROC": "STORED_PROCEDURE",
    "UDF": "FUNCTION",
    "SCALAR_FUNCTION": "FUNCTION",
    "TABLE_VALUED_FUNCTION": "FUNCTION",
    "INLINE_TABLE_FUNCTION": "FUNCTION",
    "STAT": "STATISTICS",
    "STATS": "STATISTICS",
    "EXT_TABLE": "EXTERNAL_TABLE",
    "EXT_DATA_SOURCE": "EXTERNAL_DATA_SOURCE",
    "EXT_FILE_FORMAT": "EXTERNAL_FILE_FORMAT",
    "SEC": "SECURITY",
    "IDX": "INDEX",
}

VALID_STATUSES = {"PASSED", "FAILED", "WARNING"}

STATUS_ALIASES: dict[str, str] = {
    "SUCCESS": "PASSED",
    "SUCCEEDED": "PASSED",
    "OK": "PASSED",
    "PASS": "PASSED",
    "FAIL": "FAILED",
    "ERROR": "FAILED",
    "ERRORED": "FAILED",
    "WARN": "WARNING",
    "CAUTION": "WARNING",
}


@dataclass
class AssessmentObject:
    """Represents a single database object from the migration assessment."""

    name: str
    object_type: str  # TABLE, VIEW, STORED_PROCEDURE, FUNCTION, etc.
    schema_name: str
    status: str  # Passed, Failed, Warning
    failure_reason: str = ""
    dependencies: list[str] = field(default_factory=list)
    impact_score: int = 0
    failure_category: str = ""

    @property
    def qualified_name(self) -> str:
        """Return the fully qualified name: schema.name."""
        return f"{self.schema_name}.{self.name}"

    @property
    def is_failed(self) -> bool:
        """Return True if the object failed assessment."""
        return self.status.upper() == "FAILED"

    @property
    def is_warning(self) -> bool:
        """Return True if the object has a warning status."""
        return self.status.upper() == "WARNING"

    @property
    def is_passed(self) -> bool:
        """Return True if the object passed assessment."""
        return self.status.upper() == "PASSED"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for JSON output."""
        return {
            "name": self.name,
            "qualified_name": self.qualified_name,
            "object_type": self.object_type,
            "schema_name": self.schema_name,
            "status": self.status,
            "failure_reason": self.failure_reason,
            "dependencies": self.dependencies,
            "impact_score": self.impact_score,
            "failure_category": self.failure_category,
        }


class AssessmentParser:
    """Parser for migration assessment output files.

    Supports CSV and JSON input formats with configurable column mappings.
    Normalizes object types, statuses, and dependency references for
    downstream analysis.
    """

    # Default column mappings when no config is provided
    DEFAULT_COLUMN_MAPPINGS: dict[str, str] = {
        "object_name": "ObjectName",
        "object_type": "ObjectType",
        "schema_name": "SchemaName",
        "status": "MigrationStatus",
        "failure_reason": "FailureReason",
        "dependencies": "Dependencies",
    }

    def __init__(self, column_mappings: dict[str, str] | None = None) -> None:
        """Initialize parser with optional column mappings.

        Args:
            column_mappings: Dictionary mapping logical field names to actual
                column names in the input file. If None, uses defaults.
        """
        self.column_mappings = column_mappings or self.DEFAULT_COLUMN_MAPPINGS.copy()

    def parse(
        self, file_path: str, format: str = "auto"
    ) -> list[AssessmentObject]:
        """Parse an assessment file and return a list of AssessmentObjects.

        Args:
            file_path: Path to the input file (CSV or JSON).
            format: Input format. Use "auto" to detect from file extension,
                or specify "csv" or "json" explicitly.

        Returns:
            List of parsed and validated AssessmentObject instances.

        Raises:
            FileNotFoundError: If the input file does not exist.
            ValueError: If the format is unsupported or auto-detection fails.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Assessment file not found: {file_path}")

        if format == "auto":
            ext = path.suffix.lower()
            if ext == ".csv":
                format = "csv"
            elif ext == ".json":
                format = "json"
            else:
                raise ValueError(
                    f"Cannot auto-detect format for extension '{ext}'. "
                    "Supported extensions: .csv, .json. "
                    "Use --format to specify explicitly."
                )

        logger.info("Parsing %s file: %s", format.upper(), file_path)

        if format == "csv":
            objects = self._parse_csv(file_path, self.column_mappings)
        elif format == "json":
            objects = self._parse_json(file_path)
        else:
            raise ValueError(
                f"Unsupported format: '{format}'. Use 'csv' or 'json'."
            )

        validated = self._validate_objects(objects)
        logger.info(
            "Parsed %d objects (%d after validation/dedup)",
            len(objects),
            len(validated),
        )
        return validated

    def _parse_csv(
        self, file_path: str, column_mappings: dict[str, str]
    ) -> list[AssessmentObject]:
        """Parse a CSV assessment file using pandas.

        Args:
            file_path: Path to the CSV file.
            column_mappings: Mapping of logical names to CSV column names.

        Returns:
            List of AssessmentObject instances (not yet validated).
        """
        df = pd.read_csv(file_path, dtype=str, keep_default_na=False)
        logger.debug("CSV loaded with %d rows, columns: %s", len(df), list(df.columns))

        # Build reverse mapping: actual column name -> logical field name
        available_columns = set(df.columns)
        resolved: dict[str, str] = {}
        for logical_name, csv_name in column_mappings.items():
            if csv_name in available_columns:
                resolved[logical_name] = csv_name
            else:
                # Try case-insensitive match
                match = next(
                    (c for c in available_columns if c.lower() == csv_name.lower()),
                    None,
                )
                if match:
                    resolved[logical_name] = match
                    logger.debug(
                        "Column '%s' matched case-insensitively to '%s'",
                        csv_name,
                        match,
                    )
                else:
                    logger.warning(
                        "Expected column '%s' (for %s) not found in CSV. "
                        "Available: %s. Will use empty default.",
                        csv_name,
                        logical_name,
                        sorted(available_columns),
                    )

        objects: list[AssessmentObject] = []
        for idx, row in df.iterrows():
            try:
                name = str(row.get(resolved.get("object_name", ""), "")).strip()
                if not name:
                    logger.warning("Row %d: missing object name, skipping.", idx)
                    continue

                object_type = str(
                    row.get(resolved.get("object_type", ""), "UNKNOWN")
                ).strip()
                schema_name = str(
                    row.get(resolved.get("schema_name", ""), "dbo")
                ).strip()
                status = str(
                    row.get(resolved.get("status", ""), "UNKNOWN")
                ).strip()
                failure_reason = str(
                    row.get(resolved.get("failure_reason", ""), "")
                ).strip()

                # Parse dependencies from semicolon-delimited string
                dep_raw = str(
                    row.get(resolved.get("dependencies", ""), "")
                ).strip()
                dependencies = [
                    d.strip()
                    for d in dep_raw.split(";")
                    if d.strip()
                ]

                obj = AssessmentObject(
                    name=name,
                    object_type=object_type,
                    schema_name=schema_name if schema_name else "dbo",
                    status=status,
                    failure_reason=failure_reason,
                    dependencies=dependencies,
                )
                objects.append(obj)

            except Exception as exc:
                logger.error("Row %d: failed to parse - %s", idx, exc)

        return objects

    def _parse_json(self, file_path: str) -> list[AssessmentObject]:
        """Parse a JSON assessment file.

        Expects a JSON array of objects with fields matching the
        AssessmentObject dataclass.

        Args:
            file_path: Path to the JSON file.

        Returns:
            List of AssessmentObject instances (not yet validated).
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            # Support wrapper format: { "objects": [...] }
            if "objects" in data:
                data = data["objects"]
            else:
                raise ValueError(
                    "JSON file must contain an array or an object with "
                    "an 'objects' key containing an array."
                )

        if not isinstance(data, list):
            raise ValueError(
                f"Expected JSON array, got {type(data).__name__}."
            )

        # Required fields in JSON input
        required_fields = {"name", "object_type", "schema_name", "status"}

        objects: list[AssessmentObject] = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                logger.warning("Item %d: expected object, got %s, skipping.", idx, type(item).__name__)
                continue

            # Check required fields
            missing = required_fields - set(item.keys())
            if missing:
                logger.warning(
                    "Item %d (%s): missing required fields %s, skipping.",
                    idx,
                    item.get("name", "UNKNOWN"),
                    missing,
                )
                continue

            dependencies = item.get("dependencies", [])
            if isinstance(dependencies, str):
                dependencies = [d.strip() for d in dependencies.split(";") if d.strip()]

            obj = AssessmentObject(
                name=str(item["name"]).strip(),
                object_type=str(item["object_type"]).strip(),
                schema_name=str(item["schema_name"]).strip() or "dbo",
                status=str(item["status"]).strip(),
                failure_reason=str(item.get("failure_reason", "")).strip(),
                dependencies=dependencies if isinstance(dependencies, list) else [],
            )
            objects.append(obj)

        return objects

    def _validate_objects(
        self, objects: list[AssessmentObject]
    ) -> list[AssessmentObject]:
        """Validate and normalize a list of AssessmentObjects.

        Normalizes object types to uppercase canonical names, normalizes
        status values, and deduplicates by qualified name (keeping the
        last occurrence).

        Args:
            objects: Raw parsed objects.

        Returns:
            Validated, normalized, deduplicated list.
        """
        validated: list[AssessmentObject] = []

        for obj in objects:
            # Normalize object type
            raw_type = obj.object_type.upper().replace(" ", "_")
            if raw_type in TYPE_ALIASES:
                obj.object_type = TYPE_ALIASES[raw_type]
            elif raw_type in VALID_OBJECT_TYPES:
                obj.object_type = raw_type
            else:
                logger.warning(
                    "Object '%s': unrecognized type '%s', keeping as-is.",
                    obj.name,
                    raw_type,
                )
                obj.object_type = raw_type

            # Normalize status
            raw_status = obj.status.upper().strip()
            if raw_status in STATUS_ALIASES:
                obj.status = STATUS_ALIASES[raw_status]
            elif raw_status in VALID_STATUSES:
                obj.status = raw_status
            else:
                logger.warning(
                    "Object '%s': unrecognized status '%s', treating as WARNING.",
                    obj.qualified_name,
                    raw_status,
                )
                obj.status = "WARNING"

            # Ensure schema defaults to dbo
            if not obj.schema_name:
                obj.schema_name = "dbo"

            validated.append(obj)

        # Deduplicate by qualified name, keeping last occurrence
        seen: dict[str, int] = {}
        for idx, obj in enumerate(validated):
            key = obj.qualified_name.lower()
            if key in seen:
                logger.debug(
                    "Duplicate object '%s' at index %d (first at %d), "
                    "keeping latest.",
                    obj.qualified_name,
                    idx,
                    seen[key],
                )
            seen[key] = idx

        unique_indices = sorted(seen.values())
        result = [validated[i] for i in unique_indices]

        if len(result) < len(validated):
            logger.info(
                "Deduplication removed %d duplicate(s).",
                len(validated) - len(result),
            )

        return result
