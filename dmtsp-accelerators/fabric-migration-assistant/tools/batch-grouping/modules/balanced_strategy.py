"""Balanced batch assignment strategy."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from .models import BatchPlan, Batch, DatabaseObject, ObjectType
from .dependency_graph import DependencyGraph


# Type groups and their constituent ObjectTypes
FOUNDATION_TYPES = {ObjectType.SCHEMA, ObjectType.SECURITY, ObjectType.FUNCTION}
TABLE_TYPES = {ObjectType.TABLE}
VIEW_TYPES = {ObjectType.VIEW}
PROCEDURE_TYPES = {ObjectType.STORED_PROCEDURE}
CLEANUP_TYPES = {
    ObjectType.STATISTICS,
    ObjectType.EXTERNAL_TABLE,
    ObjectType.EXTERNAL_DATA_SOURCE,
    ObjectType.EXTERNAL_FILE_FORMAT,
}


class BalancedBatchingStrategy:
    """Creates an optimized migration batch plan with balanced object distribution.

    The strategy groups objects by type (foundation, table, view, procedure, cleanup),
    partitions large groups into balanced sub-batches respecting dependency ordering,
    assigns sprint numbers, and validates inter-batch dependency consistency.
    """

    def __init__(self, config: dict) -> None:
        """Initialize with batching configuration.

        Args:
            config: Configuration dictionary typically loaded from config.yaml.
                Expected keys:
                - batching.table_batch_count (int)
                - batching.view_batch_count (int)
                - batching.balance_tolerance (int, percentage)
                - batching.min_batch_size (int)
                - ordering.sprint_mapping (dict)
        """
        batching = config.get("batching", {})
        self._table_batch_count: int = batching.get("table_batch_count", 4)
        self._view_batch_count: int = batching.get("view_batch_count", 2)
        self._balance_tolerance: int = batching.get("balance_tolerance", 20)
        self._min_batch_size: int = batching.get("min_batch_size", 3)
        self._sprint_mapping: dict = config.get("ordering", {}).get(
            "sprint_mapping",
            {
                "foundation": 1,
                "table_batches": [2, 3, 4, 5],
                "view_batches": [6, 7],
                "procedures": 8,
                "cleanup": 9,
            },
        )
        self._circular_resolution: str = config.get("dependency", {}).get(
            "circular_resolution", "warn"
        )

    def create_plan(
        self,
        objects: list[DatabaseObject],
        graph: DependencyGraph,
        engagement_name: str = "",
    ) -> BatchPlan:
        """Create a complete batch plan from assessed database objects.

        Orchestrates the full batching workflow:
        1. Separate objects by type group (foundation, tables, views, procedures, cleanup)
        2. Create foundation batch (schemas, security, functions) -> sprint 1
        3. Partition tables into N balanced batches respecting dependencies -> sprints 2-5
        4. Partition views into M balanced batches respecting dependencies -> sprints 6-7
        5. Create procedure batch -> sprint 8
        6. Create cleanup batch (statistics, external objects) -> sprint 9
        7. Set inter-batch dependencies
        8. Validate balance tolerance
        9. Return BatchPlan

        Args:
            objects: List of DatabaseObject instances from assessment parsing.
            graph: Pre-built DependencyGraph for these objects.
            engagement_name: Optional engagement name for report metadata.

        Returns:
            A fully populated BatchPlan with batches, sprints, and dependency info.
        """
        warnings: list[str] = []
        batches: list[Batch] = []
        batch_id_counter = 1

        # -- 1. Separate objects by type group --
        foundation_objs: list[DatabaseObject] = []
        table_objs: list[DatabaseObject] = []
        view_objs: list[DatabaseObject] = []
        procedure_objs: list[DatabaseObject] = []
        cleanup_objs: list[DatabaseObject] = []

        for obj in objects:
            if obj.object_type in FOUNDATION_TYPES:
                foundation_objs.append(obj)
            elif obj.object_type in TABLE_TYPES:
                table_objs.append(obj)
            elif obj.object_type in VIEW_TYPES:
                view_objs.append(obj)
            elif obj.object_type in PROCEDURE_TYPES:
                procedure_objs.append(obj)
            elif obj.object_type in CLEANUP_TYPES:
                cleanup_objs.append(obj)
            else:
                cleanup_objs.append(obj)
                warnings.append(
                    f"Object '{obj.qualified_name}' has unrecognized type "
                    f"'{obj.object_type.value}'; assigned to cleanup batch."
                )

        # -- Handle cycles --
        cycles = graph.detect_cycles()
        if cycles:
            for cycle in cycles:
                cycle_str = " -> ".join(cycle)
                msg = f"Circular dependency detected: {cycle_str}"
                if self._circular_resolution == "error":
                    raise ValueError(msg)
                elif self._circular_resolution == "warn":
                    warnings.append(msg)
                # "break" mode: we just warn and let topological sort handle it best-effort

        # -- 2. Foundation batch --
        foundation_sprint = self._sprint_mapping.get("foundation", 1)
        if foundation_objs:
            foundation_batch = Batch(
                batch_id=batch_id_counter,
                batch_name="Foundation",
                sprint_number=foundation_sprint,
                object_type_group="foundation",
                objects=sorted(foundation_objs, key=lambda o: o.qualified_name),
                dependencies=[],
            )
            batches.append(foundation_batch)
            batch_id_counter += 1
        else:
            warnings.append("No foundation objects (schemas, security, functions) found.")

        foundation_batch_ids = [b.batch_id for b in batches if b.object_type_group == "foundation"]

        # -- 3. Table batches --
        table_sprint_list = self._sprint_mapping.get("table_batches", [2, 3, 4, 5])
        actual_table_batch_count = self._determine_batch_count(
            table_objs, self._table_batch_count
        )

        if table_objs:
            table_partitions = self._partition_balanced(
                table_objs, actual_table_batch_count, graph
            )
            for i, partition in enumerate(table_partitions):
                sprint_num = (
                    table_sprint_list[i]
                    if i < len(table_sprint_list)
                    else table_sprint_list[-1] + (i - len(table_sprint_list) + 1)
                )
                tb = Batch(
                    batch_id=batch_id_counter,
                    batch_name=f"Table Batch {i + 1}",
                    sprint_number=sprint_num,
                    object_type_group="table",
                    objects=partition,
                    dependencies=list(foundation_batch_ids),
                )
                batches.append(tb)
                batch_id_counter += 1

        table_batch_ids = [b.batch_id for b in batches if b.object_type_group == "table"]

        # -- 4. View batches --
        view_sprint_list = self._sprint_mapping.get("view_batches", [6, 7])
        actual_view_batch_count = self._determine_batch_count(
            view_objs, self._view_batch_count
        )

        if view_objs:
            view_partitions = self._partition_balanced(
                view_objs, actual_view_batch_count, graph
            )
            for i, partition in enumerate(view_partitions):
                sprint_num = (
                    view_sprint_list[i]
                    if i < len(view_sprint_list)
                    else view_sprint_list[-1] + (i - len(view_sprint_list) + 1)
                )
                vb = Batch(
                    batch_id=batch_id_counter,
                    batch_name=f"View Batch {i + 1}",
                    sprint_number=sprint_num,
                    object_type_group="view",
                    objects=partition,
                    dependencies=list(table_batch_ids) + list(foundation_batch_ids),
                )
                batches.append(vb)
                batch_id_counter += 1

        view_batch_ids = [b.batch_id for b in batches if b.object_type_group == "view"]

        # -- 5. Procedure batch --
        proc_sprint = self._sprint_mapping.get("procedures", 8)
        if procedure_objs:
            proc_batch = Batch(
                batch_id=batch_id_counter,
                batch_name="Stored Procedures",
                sprint_number=proc_sprint,
                object_type_group="procedure",
                objects=sorted(procedure_objs, key=lambda o: o.qualified_name),
                dependencies=list(table_batch_ids) + list(view_batch_ids) + list(foundation_batch_ids),
            )
            batches.append(proc_batch)
            batch_id_counter += 1

        procedure_batch_ids = [b.batch_id for b in batches if b.object_type_group == "procedure"]

        # -- 6. Cleanup batch --
        cleanup_sprint = self._sprint_mapping.get("cleanup", 9)
        if cleanup_objs:
            cleanup_batch = Batch(
                batch_id=batch_id_counter,
                batch_name="Cleanup & External",
                sprint_number=cleanup_sprint,
                object_type_group="cleanup",
                objects=sorted(cleanup_objs, key=lambda o: o.qualified_name),
                dependencies=(
                    list(foundation_batch_ids)
                    + list(table_batch_ids)
                    + list(view_batch_ids)
                    + list(procedure_batch_ids)
                ),
            )
            batches.append(cleanup_batch)
            batch_id_counter += 1

        # -- 7. Validate balance tolerance --
        balance_warnings = self._validate_balance(batches)
        warnings.extend(balance_warnings)

        # -- 8. Validate batch dependencies --
        dep_warnings = self._validate_batch_dependencies(batches, graph)
        warnings.extend(dep_warnings)

        # -- 9. Build final plan --
        total_objects = sum(b.total_objects for b in batches)
        sprint_numbers = {b.sprint_number for b in batches}

        plan = BatchPlan(
            engagement_name=engagement_name,
            created_at=datetime.now(timezone.utc).isoformat(),
            total_objects=total_objects,
            total_batches=len(batches),
            total_sprints=len(sprint_numbers),
            batches=batches,
            dependency_summary=graph.summary(),
            warnings=warnings,
        )

        return plan

    def _determine_batch_count(
        self, objects: list[DatabaseObject], desired_count: int
    ) -> int:
        """Determine actual batch count, respecting minimum batch size.

        If splitting into the desired count would create batches smaller than
        the minimum, reduce the number of batches.

        Args:
            objects: Objects to be distributed.
            desired_count: Configured number of batches.

        Returns:
            Adjusted batch count (at least 1 if there are objects).
        """
        if not objects:
            return 0
        count = desired_count
        while count > 1 and len(objects) / count < self._min_batch_size:
            count -= 1
        return max(count, 1)

    def _partition_balanced(
        self,
        objects: list[DatabaseObject],
        num_batches: int,
        graph: DependencyGraph,
    ) -> list[list[DatabaseObject]]:
        """Partition objects into balanced batches respecting dependency order.

        Algorithm:
        1. Sort objects by dependency layer (layer 0 first)
        2. Within each layer, sort by impact_score descending (distribute high-impact evenly)
        3. Round-robin assignment, respecting: if A depends on B, A must be in
           the same or a later batch than B
        4. Check balance; if any batch exceeds tolerance, rebalance by moving
           lowest-impact objects from oversized batches to undersized ones

        Args:
            objects: List of DatabaseObject instances of the same type group.
            num_batches: Number of batches to partition into.
            graph: Dependency graph for ordering constraints.

        Returns:
            List of lists, where each inner list is the objects for one batch.
        """
        if num_batches <= 0:
            return []
        if num_batches == 1:
            return [list(objects)]

        # Build layer lookup for the objects in this partition
        all_layers = graph.get_layers()
        node_to_layer: dict[str, int] = {}
        for layer_idx, layer_nodes in enumerate(all_layers):
            for node in layer_nodes:
                node_to_layer[node] = layer_idx

        # Sort: primary by layer (ascending), secondary by impact_score (descending)
        sorted_objs = sorted(
            objects,
            key=lambda o: (
                node_to_layer.get(o.qualified_name, 999),
                -o.impact_score,
                o.qualified_name,
            ),
        )

        # Round-robin assignment with dependency constraint
        partitions: list[list[DatabaseObject]] = [[] for _ in range(num_batches)]
        obj_to_batch: dict[str, int] = {}

        for obj in sorted_objs:
            # Find the minimum batch index this object can go into
            # based on its dependencies within this type group
            min_batch = 0
            for dep_name in obj.dependencies:
                if dep_name in obj_to_batch:
                    min_batch = max(min_batch, obj_to_batch[dep_name])

            # Among valid batches (>= min_batch), pick the one with fewest objects
            best_batch = min_batch
            best_size = len(partitions[min_batch]) if min_batch < num_batches else float("inf")
            for bi in range(min_batch, num_batches):
                if len(partitions[bi]) < best_size:
                    best_size = len(partitions[bi])
                    best_batch = bi

            partitions[best_batch].append(obj)
            obj_to_batch[obj.qualified_name] = best_batch

        # Rebalance if needed
        partitions = self._rebalance(partitions, obj_to_batch, graph)

        return partitions

    def _rebalance(
        self,
        partitions: list[list[DatabaseObject]],
        obj_to_batch: dict[str, int],
        graph: DependencyGraph,
    ) -> list[list[DatabaseObject]]:
        """Rebalance partitions if any exceed the tolerance threshold.

        Moves lowest-impact objects from oversized batches to undersized batches,
        respecting dependency constraints (an object can only move to a batch
        index >= the batch index of all its dependencies within the partition).

        Args:
            partitions: Current partition assignment.
            obj_to_batch: Mapping of qualified name to batch index.
            graph: Dependency graph for constraint checking.

        Returns:
            Rebalanced partitions.
        """
        if not partitions:
            return partitions

        total = sum(len(p) for p in partitions)
        num_batches = len(partitions)
        if num_batches == 0 or total == 0:
            return partitions

        ideal_size = total / num_batches
        if ideal_size == 0:
            return partitions

        max_iterations = total  # Safety bound to prevent infinite loops

        for _ in range(max_iterations):
            sizes = [len(p) for p in partitions]
            max_size = max(sizes)
            min_size = min(sizes)

            if ideal_size == 0:
                break

            imbalance = ((max_size - min_size) / ideal_size) * 100
            if imbalance <= self._balance_tolerance:
                break

            # Find the most oversized batch and the most undersized batch
            largest_idx = sizes.index(max_size)
            smallest_idx = sizes.index(min_size)

            if largest_idx == smallest_idx:
                break

            # Try to move the lowest-impact object from largest to smallest
            # that doesn't violate dependency constraints
            candidates = sorted(
                partitions[largest_idx],
                key=lambda o: (o.impact_score, o.qualified_name),
            )

            moved = False
            for candidate in candidates:
                # Check: can this object be in a batch with index smallest_idx?
                # It must be >= all its dependency batch indices
                can_move = True

                # If smallest_idx < largest_idx, check dependencies don't require
                # it to be at largest_idx or later
                if smallest_idx < largest_idx:
                    for dep_name in candidate.dependencies:
                        dep_batch = obj_to_batch.get(dep_name, -1)
                        if dep_batch > smallest_idx:
                            can_move = False
                            break

                # Also check no object in a later batch depends on this one being
                # at the current position. If we move it earlier, that's fine for
                # dependents (they are already in >= current batch). But if we
                # move it later, dependents might be in an earlier batch.
                if smallest_idx > largest_idx:
                    for dependent_name in graph.get_dependents(candidate.qualified_name):
                        dep_batch = obj_to_batch.get(dependent_name, num_batches)
                        if dep_batch < smallest_idx:
                            can_move = False
                            break

                if can_move:
                    partitions[largest_idx].remove(candidate)
                    partitions[smallest_idx].append(candidate)
                    obj_to_batch[candidate.qualified_name] = smallest_idx
                    moved = True
                    break

            if not moved:
                break  # No valid move found, stop rebalancing

        return partitions

    def _validate_batch_dependencies(
        self, batches: list[Batch], graph: DependencyGraph
    ) -> list[str]:
        """Validate that no object in batch N depends on an object in batch N+1 or later.

        Checks all objects in each batch and verifies their dependencies are
        in the same or an earlier batch (lower batch_id).

        Args:
            batches: List of Batch instances in the plan.
            graph: Dependency graph for looking up dependencies.

        Returns:
            List of warning strings for any violations found.
        """
        warnings: list[str] = []

        # Build object -> batch mapping
        obj_to_batch: dict[str, int] = {}
        for batch in batches:
            for obj in batch.objects:
                obj_to_batch[obj.qualified_name] = batch.batch_id

        # Check each object's dependencies
        for batch in batches:
            for obj in batch.objects:
                deps = graph.get_dependencies(obj.qualified_name)
                for dep_name in deps:
                    dep_batch_id = obj_to_batch.get(dep_name)
                    if dep_batch_id is not None and dep_batch_id > batch.batch_id:
                        dep_batch_name = ""
                        for b in batches:
                            if b.batch_id == dep_batch_id:
                                dep_batch_name = b.batch_name
                                break
                        warnings.append(
                            f"Dependency violation: '{obj.qualified_name}' in "
                            f"'{batch.batch_name}' (batch {batch.batch_id}) depends on "
                            f"'{dep_name}' in '{dep_batch_name}' (batch {dep_batch_id}). "
                            f"'{dep_name}' should be in an earlier batch."
                        )

        return warnings

    def _validate_balance(self, batches: list[Batch]) -> list[str]:
        """Check balance within each type group.

        Args:
            batches: All batches in the plan.

        Returns:
            List of warning strings for groups that exceed balance tolerance.
        """
        warnings: list[str] = []

        # Group batches by type group
        groups: dict[str, list[Batch]] = {}
        for b in batches:
            groups.setdefault(b.object_type_group, []).append(b)

        for group_name, group_batches in groups.items():
            if len(group_batches) <= 1:
                continue

            sizes = [b.total_objects for b in group_batches]
            if not sizes:
                continue

            avg_size = sum(sizes) / len(sizes)
            if avg_size == 0:
                continue

            max_size = max(sizes)
            min_size = min(sizes)
            imbalance = ((max_size - min_size) / avg_size) * 100

            if imbalance > self._balance_tolerance:
                warnings.append(
                    f"Balance warning for '{group_name}' batches: "
                    f"size range {min_size}-{max_size} "
                    f"({imbalance:.1f}% imbalance exceeds {self._balance_tolerance}% tolerance). "
                    f"Sizes: {sizes}"
                )

        return warnings

    def _assign_sprints(self, batches: list[Batch], sprint_mapping: dict) -> list[Batch]:
        """Map batch type groups to sprint numbers from configuration.

        This is called internally during create_plan but exposed for
        re-assignment if sprint mapping changes.

        Args:
            batches: List of Batch instances to assign sprints to.
            sprint_mapping: Dictionary mapping type groups to sprint numbers.

        Returns:
            Updated list of batches with sprint_number set.
        """
        table_sprints = sprint_mapping.get("table_batches", [2, 3, 4, 5])
        view_sprints = sprint_mapping.get("view_batches", [6, 7])

        table_idx = 0
        view_idx = 0

        for batch in batches:
            if batch.object_type_group == "foundation":
                batch.sprint_number = sprint_mapping.get("foundation", 1)
            elif batch.object_type_group == "table":
                if table_idx < len(table_sprints):
                    batch.sprint_number = table_sprints[table_idx]
                else:
                    batch.sprint_number = table_sprints[-1] + (table_idx - len(table_sprints) + 1)
                table_idx += 1
            elif batch.object_type_group == "view":
                if view_idx < len(view_sprints):
                    batch.sprint_number = view_sprints[view_idx]
                else:
                    batch.sprint_number = view_sprints[-1] + (view_idx - len(view_sprints) + 1)
                view_idx += 1
            elif batch.object_type_group == "procedure":
                batch.sprint_number = sprint_mapping.get("procedures", 8)
            elif batch.object_type_group == "cleanup":
                batch.sprint_number = sprint_mapping.get("cleanup", 9)

        return batches
