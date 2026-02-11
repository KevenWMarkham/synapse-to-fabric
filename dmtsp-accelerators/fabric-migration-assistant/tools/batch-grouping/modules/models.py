"""Data models for batch grouping."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json
from datetime import datetime, timezone
from pathlib import Path


class ObjectType(Enum):
    """Database object types in migration priority order."""

    SCHEMA = "SCHEMA"
    TABLE = "TABLE"
    VIEW = "VIEW"
    STORED_PROCEDURE = "STORED_PROCEDURE"
    FUNCTION = "FUNCTION"
    STATISTICS = "STATISTICS"
    EXTERNAL_TABLE = "EXTERNAL_TABLE"
    EXTERNAL_DATA_SOURCE = "EXTERNAL_DATA_SOURCE"
    EXTERNAL_FILE_FORMAT = "EXTERNAL_FILE_FORMAT"
    SECURITY = "SECURITY"

    @classmethod
    def from_string(cls, value: str) -> "ObjectType":
        """Parse an ObjectType from a string, handling common variations.

        Args:
            value: The string representation of the object type.

        Returns:
            The matching ObjectType enum member.

        Raises:
            ValueError: If the string does not match any known object type.
        """
        normalized = value.strip().upper().replace(" ", "_").replace("-", "_")
        # Handle common aliases
        aliases = {
            "PROC": "STORED_PROCEDURE",
            "PROCEDURE": "STORED_PROCEDURE",
            "SP": "STORED_PROCEDURE",
            "STORED_PROC": "STORED_PROCEDURE",
            "UDF": "FUNCTION",
            "USER_DEFINED_FUNCTION": "FUNCTION",
            "SCALAR_FUNCTION": "FUNCTION",
            "TABLE_VALUED_FUNCTION": "FUNCTION",
            "EXT_TABLE": "EXTERNAL_TABLE",
            "EXT_DATA_SOURCE": "EXTERNAL_DATA_SOURCE",
            "EXT_FILE_FORMAT": "EXTERNAL_FILE_FORMAT",
            "STATS": "STATISTICS",
            "ROLE": "SECURITY",
            "USER": "SECURITY",
            "PERMISSION": "SECURITY",
            "DATABASE_ROLE": "SECURITY",
        }
        resolved = aliases.get(normalized, normalized)
        try:
            return cls(resolved)
        except ValueError:
            valid = ", ".join(m.value for m in cls)
            raise ValueError(
                f"Unknown object type '{value}'. Valid types: {valid}"
            ) from None


@dataclass
class DatabaseObject:
    """Represents a single database object from the assessment output.

    Attributes:
        name: The unqualified object name.
        object_type: The ObjectType classification.
        schema_name: The schema this object belongs to.
        status: Assessment status, typically 'Passed' or 'Failed'.
        failure_reason: Description of why the object failed assessment.
        dependencies: List of qualified names this object depends on.
        failure_category: Triage category (auto_fixable, minor_manual, significant_refactor).
        impact_score: Numeric score indicating how many downstream objects depend on this one.
    """

    name: str
    object_type: ObjectType
    schema_name: str
    status: str
    failure_reason: str = ""
    dependencies: list[str] = field(default_factory=list)
    failure_category: str = ""
    impact_score: int = 0

    @property
    def qualified_name(self) -> str:
        """Return the fully qualified name as schema.name."""
        return f"{self.schema_name}.{self.name}"

    @property
    def passed(self) -> bool:
        """Return True if the object passed assessment."""
        return self.status.lower() == "passed"

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "name": self.name,
            "object_type": self.object_type.value,
            "schema_name": self.schema_name,
            "qualified_name": self.qualified_name,
            "status": self.status,
            "failure_reason": self.failure_reason,
            "dependencies": self.dependencies,
            "failure_category": self.failure_category,
            "impact_score": self.impact_score,
        }


@dataclass
class Batch:
    """Represents a migration batch containing related database objects.

    Attributes:
        batch_id: Unique numeric identifier for this batch.
        batch_name: Human-readable name (e.g., 'Table Batch 1').
        sprint_number: The sprint this batch is assigned to.
        object_type_group: Category grouping (foundation, table, view, procedure, cleanup).
        objects: List of DatabaseObject instances in this batch.
        dependencies: List of batch_ids that this batch depends on.
    """

    batch_id: int
    batch_name: str
    sprint_number: int
    object_type_group: str
    objects: list[DatabaseObject] = field(default_factory=list)
    dependencies: list[int] = field(default_factory=list)

    @property
    def total_objects(self) -> int:
        """Return the total number of objects in this batch."""
        return len(self.objects)

    @property
    def passed_count(self) -> int:
        """Return the count of objects that passed assessment."""
        return sum(1 for obj in self.objects if obj.passed)

    @property
    def failed_count(self) -> int:
        """Return the count of objects that failed assessment."""
        return sum(1 for obj in self.objects if not obj.passed)

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "batch_id": self.batch_id,
            "batch_name": self.batch_name,
            "sprint_number": self.sprint_number,
            "object_type_group": self.object_type_group,
            "total_objects": self.total_objects,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "dependencies": self.dependencies,
            "objects": [obj.to_dict() for obj in self.objects],
        }


@dataclass
class BatchPlan:
    """Complete migration batch plan with all batches, dependencies, and metadata.

    Attributes:
        engagement_name: Name of the client engagement.
        created_at: ISO-8601 timestamp of plan creation.
        total_objects: Total number of objects across all batches.
        total_batches: Number of batches in the plan.
        total_sprints: Number of distinct sprints in the plan.
        batches: Ordered list of Batch instances.
        dependency_summary: Summary statistics from the dependency graph.
        warnings: List of warning messages generated during planning.
    """

    engagement_name: str = ""
    created_at: str = ""
    total_objects: int = 0
    total_batches: int = 0
    total_sprints: int = 0
    batches: list[Batch] = field(default_factory=list)
    dependency_summary: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize the entire batch plan to a JSON-compatible dictionary.

        Returns:
            A dictionary suitable for JSON serialization containing all plan
            metadata, batches with their objects, dependency summary, and warnings.
        """
        passed_total = sum(b.passed_count for b in self.batches)
        failed_total = sum(b.failed_count for b in self.batches)
        pass_rate = (
            round(passed_total / self.total_objects * 100, 1)
            if self.total_objects > 0
            else 0.0
        )

        return {
            "metadata": {
                "engagement_name": self.engagement_name,
                "created_at": self.created_at,
                "total_objects": self.total_objects,
                "total_batches": self.total_batches,
                "total_sprints": self.total_sprints,
                "passed_objects": passed_total,
                "failed_objects": failed_total,
                "pass_rate_percent": pass_rate,
            },
            "batches": [b.to_dict() for b in self.batches],
            "dependency_summary": self.dependency_summary,
            "warnings": self.warnings,
        }

    @classmethod
    def from_assessment_json(cls, path: str) -> list[DatabaseObject]:
        """Parse assessment processor (E0-S2) JSON output into DatabaseObject list.

        Reads the JSON file produced by the Assessment Processor, extracts each
        object's metadata, dependencies, and impact scores, and returns a flat
        list of DatabaseObject instances ready for batch grouping.

        Args:
            path: File system path to the assessment JSON output.

        Returns:
            List of DatabaseObject instances parsed from the assessment data.

        Raises:
            FileNotFoundError: If the assessment JSON file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.
            KeyError: If required fields are missing from the JSON structure.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Assessment file not found: {path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        objects: list[DatabaseObject] = []

        # Build impact score lookup from dependency_analysis if present
        impact_scores: dict[str, int] = {}
        dep_analysis = data.get("dependency_analysis", {})
        if "impact_scores" in dep_analysis:
            impact_scores = {
                k: int(v) for k, v in dep_analysis["impact_scores"].items()
            }

        # Build failure category lookup from triage if present
        failure_categories: dict[str, str] = {}
        if "objects" in data:
            for obj_data in data["objects"]:
                cat = obj_data.get("failure_category", "")
                if cat:
                    qname = f"{obj_data.get('schema_name', 'dbo')}.{obj_data.get('name', '')}"
                    failure_categories[qname] = cat

        # Parse each object
        for obj_data in data.get("objects", []):
            name = obj_data.get("name", "")
            schema_name = obj_data.get("schema_name", "dbo")
            status = obj_data.get("status", "Passed")
            failure_reason = obj_data.get("failure_reason", "")
            failure_category = obj_data.get("failure_category", "")
            raw_type = obj_data.get("object_type", "TABLE")

            # Parse dependencies — may be a list of strings or a comma-separated string
            raw_deps = obj_data.get("dependencies", [])
            if isinstance(raw_deps, str):
                deps = [d.strip() for d in raw_deps.split(",") if d.strip()]
            elif isinstance(raw_deps, list):
                deps = [str(d).strip() for d in raw_deps if str(d).strip()]
            else:
                deps = []

            # Resolve object type
            try:
                obj_type = ObjectType.from_string(raw_type)
            except ValueError:
                obj_type = ObjectType.TABLE  # Fallback for unknown types

            qualified_name = f"{schema_name}.{name}"
            score = impact_scores.get(qualified_name, obj_data.get("impact_score", 0))

            db_obj = DatabaseObject(
                name=name,
                object_type=obj_type,
                schema_name=schema_name,
                status=status,
                failure_reason=failure_reason,
                dependencies=deps,
                failure_category=failure_category,
                impact_score=int(score),
            )
            objects.append(db_obj)

        return objects
