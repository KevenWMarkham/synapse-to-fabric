"""Dependency analysis using NetworkX directed graph."""

from __future__ import annotations

import logging
from collections import deque
from typing import Any

import networkx as nx

from .parser import AssessmentObject

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """Analyzes dependency relationships between database objects.

    Builds a directed graph where edges flow from an object to the objects
    it depends on (i.e., an edge A -> B means A depends on B). This allows
    identification of root-cause failures, cascade failures, and optimal
    migration ordering.
    """

    def __init__(
        self,
        objects: list[AssessmentObject],
        max_depth: int = 10,
        enable_impact_scoring: bool = True,
    ) -> None:
        """Initialize the dependency analyzer.

        Args:
            objects: List of assessment objects to analyze.
            max_depth: Maximum depth for dependency chain traversal.
            enable_impact_scoring: Whether to compute impact scores.
        """
        self.objects = objects
        self.max_depth = max_depth
        self.enable_impact_scoring = enable_impact_scoring

        # Index objects by qualified name for fast lookup
        self._object_map: dict[str, AssessmentObject] = {}
        for obj in objects:
            self._object_map[obj.qualified_name.lower()] = obj

        # Build the graph
        self.graph = self.build_graph(objects)

        # Compute impact scores if enabled
        if enable_impact_scoring:
            self._impact_scores = self.calculate_impact_scores()
            # Write scores back onto objects
            for obj in self.objects:
                key = obj.qualified_name.lower()
                obj.impact_score = self._impact_scores.get(key, 0)
        else:
            self._impact_scores = {}

    def build_graph(self, objects: list[AssessmentObject]) -> nx.DiGraph:
        """Build the full dependency directed graph.

        Creates a node for each object (keyed by lowercase qualified name)
        and edges from dependents to their dependencies. Also infers
        implicit dependencies based on object type conventions.

        Args:
            objects: List of assessment objects.

        Returns:
            A NetworkX DiGraph with object metadata on nodes.
        """
        graph = nx.DiGraph()

        # Add all objects as nodes
        for obj in objects:
            key = obj.qualified_name.lower()
            graph.add_node(
                key,
                name=obj.name,
                qualified_name=obj.qualified_name,
                object_type=obj.object_type,
                schema_name=obj.schema_name,
                status=obj.status,
                failure_reason=obj.failure_reason,
            )

        # Add explicit dependency edges
        all_keys = set(graph.nodes())
        for obj in objects:
            obj_key = obj.qualified_name.lower()
            for dep in obj.dependencies:
                dep_lower = dep.strip().lower()

                # If dependency is not fully qualified, try with same schema
                if "." not in dep_lower:
                    dep_lower = f"{obj.schema_name.lower()}.{dep_lower}"

                if dep_lower in all_keys:
                    # Edge: obj depends on dep (obj -> dep means obj requires dep)
                    graph.add_edge(obj_key, dep_lower, edge_type="explicit")
                else:
                    logger.debug(
                        "Dependency '%s' of '%s' not found in assessment objects.",
                        dep,
                        obj.qualified_name,
                    )

        # Infer implicit dependencies based on object type patterns
        self._add_implicit_dependencies(graph, objects)

        logger.info(
            "Dependency graph built: %d nodes, %d edges.",
            graph.number_of_nodes(),
            graph.number_of_edges(),
        )

        return graph

    def _add_implicit_dependencies(
        self, graph: nx.DiGraph, objects: list[AssessmentObject]
    ) -> None:
        """Add inferred dependency edges based on object type conventions.

        Rules:
        - VIEWs implicitly depend on TABLEs and other VIEWs in the same schema
          (if no explicit dependencies are listed and the names suggest a relationship)
        - STATISTICS objects depend on their parent TABLE
        - EXTERNAL_TABLEs depend on EXTERNAL_DATA_SOURCE objects

        Args:
            graph: The graph to add edges to (modified in place).
            objects: The list of assessment objects.
        """
        tables_by_schema: dict[str, list[str]] = {}
        ext_sources: list[str] = []

        for obj in objects:
            key = obj.qualified_name.lower()
            if obj.object_type == "TABLE":
                schema_lower = obj.schema_name.lower()
                tables_by_schema.setdefault(schema_lower, []).append(key)
            elif obj.object_type == "EXTERNAL_DATA_SOURCE":
                ext_sources.append(key)

        for obj in objects:
            obj_key = obj.qualified_name.lower()

            # STATISTICS -> TABLE: stats object names often contain the table name
            if obj.object_type == "STATISTICS":
                name_lower = obj.name.lower()
                schema_lower = obj.schema_name.lower()
                for table_key in tables_by_schema.get(schema_lower, []):
                    table_name = table_key.split(".", 1)[1] if "." in table_key else table_key
                    if table_name in name_lower:
                        if not graph.has_edge(obj_key, table_key):
                            graph.add_edge(obj_key, table_key, edge_type="implicit")
                            logger.debug(
                                "Implicit dependency: %s -> %s (statistics on table)",
                                obj.qualified_name,
                                table_key,
                            )

            # EXTERNAL_TABLE -> EXTERNAL_DATA_SOURCE
            if obj.object_type == "EXTERNAL_TABLE":
                for src_key in ext_sources:
                    if not graph.has_edge(obj_key, src_key):
                        graph.add_edge(obj_key, src_key, edge_type="implicit")
                        logger.debug(
                            "Implicit dependency: %s -> %s (external table to source)",
                            obj.qualified_name,
                            src_key,
                        )

    def _get_object(self, key: str) -> AssessmentObject | None:
        """Look up an object by qualified name (case-insensitive).

        Args:
            key: The qualified name to look up.

        Returns:
            The AssessmentObject or None if not found.
        """
        return self._object_map.get(key.lower())

    def _is_failed_node(self, node_key: str) -> bool:
        """Check if a graph node represents a failed object.

        Args:
            node_key: The node key in the graph.

        Returns:
            True if the node's status is FAILED.
        """
        data = self.graph.nodes.get(node_key, {})
        return data.get("status", "").upper() == "FAILED"

    def identify_primary_failures(self) -> list[AssessmentObject]:
        """Find objects that failed with no upstream (ancestor) failures.

        Primary failures are root causes -- they failed on their own merits,
        not because something they depend on also failed.

        Returns:
            List of AssessmentObject instances that are primary failures,
            sorted by impact score descending.
        """
        primary: list[AssessmentObject] = []

        for obj in self.objects:
            if not obj.is_failed:
                continue

            obj_key = obj.qualified_name.lower()

            # Check all ancestors (objects this one depends on, transitively)
            has_upstream_failure = False
            try:
                # Successors in our graph direction = dependencies
                ancestors = self._get_ancestors(obj_key)
                for ancestor_key in ancestors:
                    if self._is_failed_node(ancestor_key):
                        has_upstream_failure = True
                        break
            except nx.NetworkXError:
                pass

            if not has_upstream_failure:
                primary.append(obj)

        # Sort by impact score descending
        primary.sort(key=lambda o: o.impact_score, reverse=True)

        logger.info("Identified %d primary failure(s).", len(primary))
        return primary

    def identify_dependent_failures(self) -> list[AssessmentObject]:
        """Find objects that failed due to upstream dependency failures.

        These are cascade failures -- they may work fine once their
        upstream dependencies are fixed.

        Returns:
            List of AssessmentObject instances that are dependent failures,
            sorted by impact score descending.
        """
        dependent: list[AssessmentObject] = []

        for obj in self.objects:
            if not obj.is_failed:
                continue

            obj_key = obj.qualified_name.lower()

            # Check for at least one upstream failure
            try:
                ancestors = self._get_ancestors(obj_key)
                has_upstream_failure = any(
                    self._is_failed_node(a) for a in ancestors
                )
                if has_upstream_failure:
                    dependent.append(obj)
            except nx.NetworkXError:
                pass

        dependent.sort(key=lambda o: o.impact_score, reverse=True)

        logger.info("Identified %d dependent failure(s).", len(dependent))
        return dependent

    def _get_ancestors(self, node_key: str) -> set[str]:
        """Get all ancestor nodes (transitive dependencies) up to max_depth.

        In our graph, an edge A -> B means A depends on B. So the
        ancestors of A (things A depends on) are found by following
        outgoing edges (successors in the DiGraph).

        Args:
            node_key: The node to find ancestors for.

        Returns:
            Set of ancestor node keys.
        """
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(node_key, 0)])

        while queue:
            current, depth = queue.popleft()
            if depth >= self.max_depth:
                continue

            for successor in self.graph.successors(current):
                if successor not in visited and successor != node_key:
                    visited.add(successor)
                    queue.append((successor, depth + 1))

        return visited

    def _get_descendants(self, node_key: str) -> set[str]:
        """Get all descendant nodes (objects that depend on this one).

        In our graph, an edge A -> B means A depends on B. So the
        descendants of B (things that depend on B) are found by following
        incoming edges (predecessors in the DiGraph).

        Args:
            node_key: The node to find descendants for.

        Returns:
            Set of descendant node keys.
        """
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(node_key, 0)])

        while queue:
            current, depth = queue.popleft()
            if depth >= self.max_depth:
                continue

            for predecessor in self.graph.predecessors(current):
                if predecessor not in visited and predecessor != node_key:
                    visited.add(predecessor)
                    queue.append((predecessor, depth + 1))

        return visited

    def calculate_impact_scores(self) -> dict[str, int]:
        """Calculate impact scores for all failed objects.

        The impact score of a failed object is the count of downstream
        objects (descendants) it blocks. Higher scores indicate higher
        priority for fixing.

        Returns:
            Dictionary mapping qualified name (lowercase) to impact score.
        """
        scores: dict[str, int] = {}

        for obj in self.objects:
            if not obj.is_failed:
                continue

            obj_key = obj.qualified_name.lower()
            descendants = self._get_descendants(obj_key)
            scores[obj_key] = len(descendants)

        logger.info(
            "Calculated impact scores for %d failed object(s). "
            "Max score: %d.",
            len(scores),
            max(scores.values()) if scores else 0,
        )
        return scores

    def get_dependency_chains(self, object_name: str) -> list[list[str]]:
        """Return all dependency paths from this object to its leaf dependents.

        Finds all objects that transitively depend on the given object
        and returns the paths from the given object to each leaf (an
        object that nothing else depends on).

        Args:
            object_name: Qualified name (schema.name) of the object.

        Returns:
            List of paths, where each path is a list of qualified names
            from the given object to a leaf dependent.
        """
        obj_key = object_name.lower()
        if obj_key not in self.graph:
            logger.warning("Object '%s' not found in dependency graph.", object_name)
            return []

        chains: list[list[str]] = []

        # Find all leaf dependents (predecessors with no further predecessors
        # that we haven't visited)
        def _dfs(
            current: str,
            path: list[str],
            visited: set[str],
            depth: int,
        ) -> None:
            if depth > self.max_depth:
                chains.append(list(path))
                return

            # Predecessors = objects that depend on current
            preds = [
                p for p in self.graph.predecessors(current)
                if p not in visited
            ]

            if not preds:
                # Leaf node -- record this chain if it has more than just the root
                if len(path) > 1:
                    chains.append(list(path))
                return

            for pred in preds:
                visited.add(pred)
                node_data = self.graph.nodes.get(pred, {})
                display_name = node_data.get("qualified_name", pred)
                path.append(display_name)
                _dfs(pred, path, visited, depth + 1)
                path.pop()
                visited.discard(pred)

        root_data = self.graph.nodes.get(obj_key, {})
        root_display = root_data.get("qualified_name", object_name)
        _dfs(obj_key, [root_display], {obj_key}, 0)

        return chains

    def get_migration_order(self) -> list[list[str]]:
        """Return a layered topological ordering for migration.

        Objects with no dependencies come first (layer 0), then objects
        that only depend on layer 0, and so on. This gives a safe
        migration order.

        Returns:
            List of layers, where each layer is a list of qualified names
            that can be migrated in parallel within the layer.
        """
        # Work with a copy to handle cycles gracefully
        if not nx.is_directed_acyclic_graph(self.graph):
            logger.warning(
                "Dependency graph contains cycles. Breaking cycles for "
                "topological ordering."
            )
            graph = self.graph.copy()
            # Remove edges that form cycles (use feedback arc set approximation)
            try:
                cycles = list(nx.simple_cycles(graph))
                for cycle in cycles:
                    if len(cycle) >= 2:
                        graph.remove_edge(cycle[0], cycle[1])
                        logger.debug(
                            "Broke cycle by removing edge: %s -> %s",
                            cycle[0],
                            cycle[1],
                        )
            except nx.NetworkXError:
                pass
        else:
            graph = self.graph

        layers: list[list[str]] = []
        remaining = set(graph.nodes())

        while remaining:
            # Find nodes with no outgoing edges to remaining nodes
            # (no unresolved dependencies)
            layer: list[str] = []
            for node in remaining:
                # Outgoing edges go to dependencies
                deps_in_remaining = [
                    s for s in graph.successors(node) if s in remaining
                ]
                if not deps_in_remaining:
                    layer.append(node)

            if not layer:
                # All remaining nodes have circular dependencies; dump them
                logger.warning(
                    "Unresolvable circular dependencies among %d objects. "
                    "Adding them all to the final layer.",
                    len(remaining),
                )
                layer = sorted(remaining)
                remaining.clear()
            else:
                for node in layer:
                    remaining.discard(node)

            # Convert keys to display names
            display_layer = []
            for key in sorted(layer):
                data = graph.nodes.get(key, {})
                display_layer.append(data.get("qualified_name", key))

            layers.append(display_layer)

        logger.info(
            "Migration order: %d layers for %d objects.",
            len(layers),
            graph.number_of_nodes(),
        )
        return layers

    def summary(self) -> dict[str, Any]:
        """Return summary statistics of the dependency analysis.

        Returns:
            Dictionary with: total_nodes, total_edges, primary_failures_count,
            dependent_failures_count, max_chain_depth, most_impactful_failures.
        """
        primary = self.identify_primary_failures()
        dependent = self.identify_dependent_failures()

        # Calculate max chain depth
        max_depth = 0
        for obj in self.objects:
            if obj.is_failed:
                chains = self.get_dependency_chains(obj.qualified_name)
                for chain in chains:
                    max_depth = max(max_depth, len(chain) - 1)

        # Top 5 most impactful failures
        failed_with_scores = [
            (obj.qualified_name, obj.impact_score, obj.failure_reason)
            for obj in self.objects
            if obj.is_failed
        ]
        failed_with_scores.sort(key=lambda x: x[1], reverse=True)
        top_5 = [
            {
                "qualified_name": name,
                "impact_score": score,
                "failure_reason": reason,
            }
            for name, score, reason in failed_with_scores[:5]
        ]

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "primary_failures_count": len(primary),
            "dependent_failures_count": len(dependent),
            "max_chain_depth": max_depth,
            "most_impactful_failures": top_5,
        }
