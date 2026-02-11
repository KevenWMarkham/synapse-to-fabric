"""Failure categorization by pattern matching."""

from __future__ import annotations

import logging
import re
from typing import Any

from .parser import AssessmentObject

logger = logging.getLogger(__name__)

# Mapping of failure reason patterns to Copilot prompt IDs from E0-S3.
# Each key is a regex pattern fragment; the value is a list of prompt IDs
# from the Copilot prompt library that address that failure type.
COPILOT_PROMPT_MAPPINGS: dict[str, list[str]] = {
    "DISTRIBUTION": ["DIST-001", "DIST-002", "DIST-003"],
    "CLUSTERED COLUMNSTORE": ["CCI-001", "CCI-002"],
    "IDENTITY": ["IDEN-001", "IDEN-002"],
    "STATISTICS": ["STAT-001"],
    "CTAS": ["CTAS-001", "CTAS-002"],
    "MATERIALIZED VIEW": ["MVIEW-001", "MVIEW-002"],
    "WORKLOAD.*CLASSIFIER": ["WLC-001"],
    "deprecated.*data type": ["DTYPE-001", "DTYPE-002"],
    "UNICODE.*collation": ["COLL-001"],
    "PARTITION": ["PART-001", "PART-002"],
    "EXTERNAL TABLE": ["EXT-001", "EXT-002"],
    "EXTERNAL.*DATA_SOURCE": ["EXT-001", "EXT-003"],
    "cross.database": ["XREF-001", "XREF-002"],
    "stored procedure.*incompatible": ["PROC-001", "PROC-002"],
    "complex.*dependency": ["DEP-001"],
}

# Default category configuration used when no config file is provided
DEFAULT_CATEGORIES: dict[str, dict[str, Any]] = {
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
}


class FailureTriage:
    """Categorizes migration failures by matching failure reasons against
    configurable regex patterns.

    Categories are ordered by fix effort:
    - auto_fixable: Copilot/scripts can resolve automatically
    - minor_manual: Less than 1 hour manual effort per object
    - significant_refactor: More than 1 hour manual effort per object
    - uncategorized: Does not match any known pattern
    """

    def __init__(
        self, categories: dict[str, dict[str, Any]] | None = None
    ) -> None:
        """Initialize the triage engine with category configuration.

        Args:
            categories: Category configuration dict from config.yaml
                analysis.categories section. Each category has 'description'
                and 'patterns' (list of regex strings). If None, uses
                built-in defaults.
        """
        self.categories = categories or DEFAULT_CATEGORIES
        self._compiled_patterns: dict[str, list[re.Pattern[str]]] = {}
        self._categorized_objects: list[AssessmentObject] = []
        self._uncategorized_reasons: list[str] = []

        # Pre-compile regex patterns for each category
        for category_name, category_config in self.categories.items():
            patterns = category_config.get("patterns", [])
            compiled: list[re.Pattern[str]] = []
            for pattern_str in patterns:
                try:
                    compiled.append(re.compile(pattern_str, re.IGNORECASE))
                except re.error as exc:
                    logger.error(
                        "Invalid regex pattern '%s' in category '%s': %s",
                        pattern_str,
                        category_name,
                        exc,
                    )
            self._compiled_patterns[category_name] = compiled

        logger.debug(
            "Triage initialized with %d categories, %d total patterns.",
            len(self.categories),
            sum(len(p) for p in self._compiled_patterns.values()),
        )

    def categorize(
        self, objects: list[AssessmentObject]
    ) -> list[AssessmentObject]:
        """Categorize each failed object's failure reason.

        For each object with status FAILED, matches the failure_reason
        against category patterns. The first matching category wins.
        Objects that match no category are labeled 'uncategorized'.

        Non-failed objects are left unchanged (failure_category remains
        empty string).

        Args:
            objects: List of assessment objects to categorize.

        Returns:
            The same list with failure_category populated on failed objects.
        """
        self._categorized_objects = objects
        self._uncategorized_reasons = []
        category_counts: dict[str, int] = {}

        for obj in objects:
            if not obj.is_failed:
                continue

            category = self._match_category(obj.failure_reason)
            obj.failure_category = category
            category_counts[category] = category_counts.get(category, 0) + 1

            if category == "uncategorized":
                self._uncategorized_reasons.append(obj.failure_reason)

        logger.info(
            "Triage results: %s",
            ", ".join(f"{k}={v}" for k, v in sorted(category_counts.items())),
        )

        return objects

    def _match_category(self, failure_reason: str) -> str:
        """Match a failure reason string against category patterns.

        Tries each category's patterns in the order they appear in the
        configuration. Returns the name of the first matching category,
        or 'uncategorized' if no pattern matches.

        Args:
            failure_reason: The failure reason text from the assessment.

        Returns:
            Category name string.
        """
        if not failure_reason:
            return "uncategorized"

        for category_name, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(failure_reason):
                    logger.debug(
                        "Failure reason '%s' matched category '%s' "
                        "(pattern: %s)",
                        failure_reason[:60],
                        category_name,
                        pattern.pattern,
                    )
                    return category_name

        return "uncategorized"

    def get_summary(self) -> dict[str, Any]:
        """Return a summary of the triage results.

        Returns:
            Dictionary containing:
            - counts: dict of category -> count
            - percentages: dict of category -> percentage of total failures
            - descriptions: dict of category -> description
            - uncategorized_reasons: list of failure reasons that didn't
              match any category (for review and pattern improvement)
            - total_failures: total number of failed objects
        """
        counts: dict[str, int] = {
            "auto_fixable": 0,
            "minor_manual": 0,
            "significant_refactor": 0,
            "uncategorized": 0,
        }

        for obj in self._categorized_objects:
            if obj.is_failed and obj.failure_category:
                counts[obj.failure_category] = (
                    counts.get(obj.failure_category, 0) + 1
                )

        total_failures = sum(counts.values())

        # Calculate percentages
        percentages: dict[str, float] = {}
        for category, count in counts.items():
            if total_failures > 0:
                percentages[category] = round(
                    (count / total_failures) * 100, 1
                )
            else:
                percentages[category] = 0.0

        # Build descriptions
        descriptions: dict[str, str] = {}
        for category_name, category_config in self.categories.items():
            descriptions[category_name] = category_config.get(
                "description", ""
            )
        descriptions["uncategorized"] = (
            "Does not match any known failure pattern"
        )

        # Deduplicate uncategorized reasons
        unique_uncategorized = sorted(set(self._uncategorized_reasons))

        return {
            "counts": counts,
            "percentages": percentages,
            "descriptions": descriptions,
            "uncategorized_reasons": unique_uncategorized,
            "total_failures": total_failures,
        }

    def suggest_copilot_prompts(
        self, objects: list[AssessmentObject]
    ) -> dict[str, list[str]]:
        """Map failed objects to relevant Copilot prompt IDs.

        Uses the COPILOT_PROMPT_MAPPINGS to match failure reason patterns
        to prompt IDs from the E0-S3 Copilot prompt library.

        Args:
            objects: List of assessment objects (should be already categorized).

        Returns:
            Dictionary mapping object qualified names to lists of
            suggested Copilot prompt IDs.
        """
        suggestions: dict[str, list[str]] = {}

        for obj in objects:
            if not obj.is_failed or not obj.failure_reason:
                continue

            matched_prompts: list[str] = []
            for pattern_str, prompt_ids in COPILOT_PROMPT_MAPPINGS.items():
                try:
                    if re.search(pattern_str, obj.failure_reason, re.IGNORECASE):
                        for pid in prompt_ids:
                            if pid not in matched_prompts:
                                matched_prompts.append(pid)
                except re.error:
                    continue

            if matched_prompts:
                suggestions[obj.qualified_name] = matched_prompts
                logger.debug(
                    "Object '%s': suggested prompts %s",
                    obj.qualified_name,
                    matched_prompts,
                )

        logger.info(
            "Generated Copilot prompt suggestions for %d object(s).",
            len(suggestions),
        )
        return suggestions
