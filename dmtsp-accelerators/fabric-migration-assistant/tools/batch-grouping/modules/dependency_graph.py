"""Directed Acyclic Graph with topological sort for migration ordering."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Optional

from .models import DatabaseObject, ObjectType


class DependencyGraph:
    """Directed graph representing migration dependencies between database objects.

    Nodes are qualified object names (schema.name). A directed edge from A to B
    means 'A depends on B' -- B must be migrated before A.

    The graph supports cycle detection (Tarjan's algorithm), topological sorting
    (Kahn's algorithm), and layer decomposition for batch grouping.
    """

    def __init__(self, objects: list[DatabaseObject]) -> None:
        """Initialize the dependency graph from a list of database objects.

        Builds the adjacency list representation and adds implicit type-based
        dependency edges.

        Args:
            objects: List of DatabaseObject instances to build the graph from.
        """
        # adjacency: node -> set of nodes it depends on (predecessors)
        self._depends_on: dict[str, set[str]] = defaultdict(set)
        # reverse adjacency: node -> set of nodes that depend on it (successors)
        self._depended_by: dict[str, set[str]] = defaultdict(set)
        # All known nodes
        self._nodes: set[str] = set()
        # Object lookup by qualified name
        self._object_map: dict[str, DatabaseObject] = {}

        for obj in objects:
            self._object_map[obj.qualified_name] = obj

        self.build(objects)
        self.add_implicit_edges(objects)

    def build(self, objects: list[DatabaseObject]) -> None:
        """Build adjacency list representation from explicit object dependencies.

        Nodes are qualified object names. Edges represent 'A depends on B',
        meaning B must migrate before A.

        Args:
            objects: List of DatabaseObject instances with their declared dependencies.
        """
        for obj in objects:
            qname = obj.qualified_name
            self._nodes.add(qname)

            for dep in obj.dependencies:
                dep_clean = dep.strip()
                if not dep_clean:
                    continue
                self._nodes.add(dep_clean)
                self._depends_on[qname].add(dep_clean)
                self._depended_by[dep_clean].add(qname)

    def add_implicit_edges(self, objects: list[DatabaseObject]) -> None:
        """Add type-based ordering edges that are implied by migration best practices.

        Implicit rules:
        - All tables depend on their schema (schema.* -> dbo schema node if exists)
        - All views depend on any tables they reference (from explicit deps)
        - All stored procedures depend on referenced tables, views, and functions
        - All objects implicitly depend on SCHEMA and SECURITY objects

        Args:
            objects: List of DatabaseObject instances to derive implicit edges from.
        """
        # Collect foundation objects
        schemas: list[str] = []
        security: list[str] = []
        functions: list[str] = []
        tables: list[str] = []

        for obj in objects:
            qname = obj.qualified_name
            if obj.object_type == ObjectType.SCHEMA:
                schemas.append(qname)
            elif obj.object_type == ObjectType.SECURITY:
                security.append(qname)
            elif obj.object_type == ObjectType.FUNCTION:
                functions.append(qname)
            elif obj.object_type == ObjectType.TABLE:
                tables.append(qname)

        for obj in objects:
            qname = obj.qualified_name

            # Tables depend on schemas being created first
            if obj.object_type == ObjectType.TABLE:
                for schema_qname in schemas:
                    schema_obj = self._object_map.get(schema_qname)
                    if schema_obj and schema_obj.name == obj.schema_name:
                        self._add_edge(qname, schema_qname)

            # Views depend on all tables they reference (explicit deps already handled)
            # Also ensure views depend on all schemas
            if obj.object_type == ObjectType.VIEW:
                for schema_qname in schemas:
                    schema_obj = self._object_map.get(schema_qname)
                    if schema_obj and schema_obj.name == obj.schema_name:
                        self._add_edge(qname, schema_qname)

            # Stored procedures depend on schemas, and any referenced functions
            if obj.object_type == ObjectType.STORED_PROCEDURE:
                for schema_qname in schemas:
                    schema_obj = self._object_map.get(schema_qname)
                    if schema_obj and schema_obj.name == obj.schema_name:
                        self._add_edge(qname, schema_qname)

            # External tables depend on external data sources
            if obj.object_type == ObjectType.EXTERNAL_TABLE:
                for other_obj in objects:
                    if other_obj.object_type == ObjectType.EXTERNAL_DATA_SOURCE:
                        self._add_edge(qname, other_obj.qualified_name)
                for other_obj in objects:
                    if other_obj.object_type == ObjectType.EXTERNAL_FILE_FORMAT:
                        self._add_edge(qname, other_obj.qualified_name)

            # Security objects depend on schemas
            if obj.object_type == ObjectType.SECURITY:
                for schema_qname in schemas:
                    self._add_edge(qname, schema_qname)

            # Functions depend on schemas
            if obj.object_type == ObjectType.FUNCTION:
                for schema_qname in schemas:
                    schema_obj = self._object_map.get(schema_qname)
                    if schema_obj and schema_obj.name == obj.schema_name:
                        self._add_edge(qname, schema_qname)

    def _add_edge(self, from_node: str, to_node: str) -> None:
        """Add a directed edge: from_node depends on to_node.

        Args:
            from_node: The dependent node (migrated after to_node).
            to_node: The prerequisite node (migrated before from_node).
        """
        if from_node == to_node:
            return
        self._nodes.add(from_node)
        self._nodes.add(to_node)
        self._depends_on[from_node].add(to_node)
        self._depended_by[to_node].add(from_node)

    def detect_cycles(self) -> list[list[str]]:
        """Detect all cycles using Tarjan's strongly connected components algorithm.

        Returns:
            List of cycles, where each cycle is a list of qualified node names
            forming a strongly connected component of size > 1. Returns an empty
            list if the graph is acyclic.
        """
        index_counter = [0]
        stack: list[str] = []
        on_stack: set[str] = set()
        indices: dict[str, int] = {}
        lowlinks: dict[str, int] = {}
        sccs: list[list[str]] = []

        def strongconnect(node: str) -> None:
            indices[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack.add(node)

            # Visit all nodes that this node depends on
            for successor in self._depends_on.get(node, set()):
                if successor not in indices:
                    strongconnect(successor)
                    lowlinks[node] = min(lowlinks[node], lowlinks[successor])
                elif successor in on_stack:
                    lowlinks[node] = min(lowlinks[node], indices[successor])

            # If node is a root node, pop the SCC
            if lowlinks[node] == indices[node]:
                scc: list[str] = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    scc.append(w)
                    if w == node:
                        break
                if len(scc) > 1:
                    sccs.append(scc)

        for node in self._nodes:
            if node not in indices:
                strongconnect(node)

        return sccs

    def topological_sort(self) -> list[str]:
        """Perform topological sort using Kahn's algorithm.

        Returns nodes in an order such that for every directed edge (A -> B),
        where A depends on B, B appears before A in the output.

        Returns:
            Ordered list of qualified node names. Nodes with no dependencies
            come first, followed by nodes whose dependencies have been satisfied.

        Raises:
            ValueError: If cycles prevent a complete topological sort.
        """
        # Compute in-degree (number of prerequisites each node has)
        in_degree: dict[str, int] = {node: 0 for node in self._nodes}
        for node in self._nodes:
            in_degree[node] = len(self._depends_on.get(node, set()))

        # Start with nodes that have no dependencies
        queue: deque[str] = deque()
        for node in sorted(self._nodes):  # sorted for deterministic output
            if in_degree[node] == 0:
                queue.append(node)

        result: list[str] = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # For each node that depends on the current node, reduce in-degree
            for dependent in sorted(self._depended_by.get(node, set())):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) < len(self._nodes):
            remaining = self._nodes - set(result)
            cycles = self.detect_cycles()
            cycle_info = ""
            if cycles:
                cycle_strs = [" -> ".join(c) for c in cycles[:3]]
                cycle_info = f" Cycles found: {'; '.join(cycle_strs)}"
            raise ValueError(
                f"Topological sort incomplete: {len(remaining)} nodes in cycles. "
                f"Unresolved: {sorted(remaining)[:10]}.{cycle_info}"
            )

        return result

    def get_layers(self) -> list[list[str]]:
        """Group nodes into dependency layers.

        Layer 0 contains all nodes with no dependencies. Layer N contains all
        nodes whose dependencies are entirely within layers 0 through N-1.

        Returns:
            List of layers, where each layer is a list of qualified node names.
            Index 0 is the first layer (no dependencies).
        """
        # Compute which layer each node belongs to
        node_layer: dict[str, int] = {}
        in_degree: dict[str, int] = {node: 0 for node in self._nodes}
        for node in self._nodes:
            in_degree[node] = len(self._depends_on.get(node, set()))

        # BFS layer by layer
        current_layer_nodes: list[str] = []
        for node in sorted(self._nodes):
            if in_degree[node] == 0:
                current_layer_nodes.append(node)
                node_layer[node] = 0

        layers: list[list[str]] = []
        if current_layer_nodes:
            layers.append(sorted(current_layer_nodes))

        while current_layer_nodes:
            next_layer_nodes: list[str] = []
            for node in current_layer_nodes:
                for dependent in sorted(self._depended_by.get(node, set())):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        next_layer_nodes.append(dependent)
                        node_layer[dependent] = len(layers)

            if next_layer_nodes:
                layers.append(sorted(next_layer_nodes))
            current_layer_nodes = next_layer_nodes

        return layers

    def get_node_layer(self, node: str) -> int:
        """Return the layer number for a specific node.

        Args:
            node: Qualified name of the node.

        Returns:
            Layer index (0-based). Returns -1 if node is not found.
        """
        layers = self.get_layers()
        for i, layer in enumerate(layers):
            if node in layer:
                return i
        return -1

    def get_ancestors(self, node: str) -> set[str]:
        """Return all transitive dependencies of a node.

        Traverses the dependency graph upstream to find every object that
        must be migrated before this node.

        Args:
            node: Qualified name of the node to trace ancestors for.

        Returns:
            Set of qualified names of all transitive dependencies.
        """
        visited: set[str] = set()
        queue: deque[str] = deque()

        for dep in self._depends_on.get(node, set()):
            queue.append(dep)

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for dep in self._depends_on.get(current, set()):
                if dep not in visited:
                    queue.append(dep)

        return visited

    def get_descendants(self, node: str) -> set[str]:
        """Return all objects that transitively depend on this node.

        Traverses the dependency graph downstream to find every object that
        requires this node to be migrated first.

        Args:
            node: Qualified name of the node to trace descendants for.

        Returns:
            Set of qualified names of all transitive dependents.
        """
        visited: set[str] = set()
        queue: deque[str] = deque()

        for dep in self._depended_by.get(node, set()):
            queue.append(dep)

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for dep in self._depended_by.get(current, set()):
                if dep not in visited:
                    queue.append(dep)

        return visited

    def get_dependencies(self, node: str) -> set[str]:
        """Return the direct dependencies of a node.

        Args:
            node: Qualified name of the node.

        Returns:
            Set of qualified names this node directly depends on.
        """
        return set(self._depends_on.get(node, set()))

    def get_dependents(self, node: str) -> set[str]:
        """Return the direct dependents of a node.

        Args:
            node: Qualified name of the node.

        Returns:
            Set of qualified names that directly depend on this node.
        """
        return set(self._depended_by.get(node, set()))

    def has_node(self, node: str) -> bool:
        """Check if a node exists in the graph.

        Args:
            node: Qualified name to check.

        Returns:
            True if the node is in the graph.
        """
        return node in self._nodes

    @property
    def nodes(self) -> set[str]:
        """Return all nodes in the graph."""
        return set(self._nodes)

    @property
    def edge_count(self) -> int:
        """Return total number of directed edges in the graph."""
        return sum(len(deps) for deps in self._depends_on.values())

    def summary(self) -> dict:
        """Generate a summary of the dependency graph.

        Returns:
            Dictionary containing:
            - total_nodes: Number of nodes in the graph
            - total_edges: Number of directed edges
            - num_layers: Number of dependency layers
            - cycle_count: Number of strongly connected components (cycles)
            - max_chain_depth: Deepest dependency chain (number of layers - 1)
            - root_nodes: Count of nodes with no dependencies
            - leaf_nodes: Count of nodes with no dependents
        """
        layers = self.get_layers()
        cycles = self.detect_cycles()

        root_count = 0
        leaf_count = 0
        for node in self._nodes:
            if not self._depends_on.get(node):
                root_count += 1
            if not self._depended_by.get(node):
                leaf_count += 1

        return {
            "total_nodes": len(self._nodes),
            "total_edges": self.edge_count,
            "num_layers": len(layers),
            "cycle_count": len(cycles),
            "cycles": [c for c in cycles],
            "max_chain_depth": max(len(layers) - 1, 0),
            "root_nodes": root_count,
            "leaf_nodes": leaf_count,
        }
