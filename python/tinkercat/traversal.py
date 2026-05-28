"""
GraphTraversalSource and GraphTraversal for TinkerCat Python bindings.

Provides a fluent traversal API over TinkerCat graphs that mirrors the
Kotlin GraphTraversal interface.  Each intermediate step returns a new
GraphTraversal; no work is performed until a terminal step is called.
"""

from __future__ import annotations
import builtins as _builtins
from typing import Any, Callable, Iterator, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from .graph import TinkerCat, Vertex, Edge


class GraphTraversal:
    """Lazy, composable traversal over TinkerCat graph elements."""

    def __init__(self, elements):
        self._pipeline = list(elements)

    # ── Filtering ─────────────────────────────────────────────────────────────

    def has_label(self, *labels: str) -> "GraphTraversal":
        return GraphTraversal(
            e for e in self._pipeline if e.label in labels
        )

    def has(self, key: str, value: Any = None) -> "GraphTraversal":
        if value is None:
            return GraphTraversal(
                e for e in self._pipeline if e.value(key) is not None
            )
        return GraphTraversal(
            e for e in self._pipeline if e.value(key) == value
        )

    def has_not(self, key: str) -> "GraphTraversal":
        return GraphTraversal(
            e for e in self._pipeline if e.value(key) is None
        )

    def has_id(self, *ids) -> "GraphTraversal":
        return GraphTraversal(
            e for e in self._pipeline if e.id in ids
        )

    # ── Vertex navigation ──────────────────────────────────────────────────────

    def out(self, *labels: str) -> "GraphTraversal":
        result = []
        for v in self._pipeline:
            result.extend(v.out_vertices(*labels))
        return GraphTraversal(result)

    def in_(self, *labels: str) -> "GraphTraversal":
        result = []
        for v in self._pipeline:
            result.extend(v.in_vertices(*labels))
        return GraphTraversal(result)

    def both(self, *labels: str) -> "GraphTraversal":
        result = []
        for v in self._pipeline:
            result.extend(v.both_vertices(*labels))
        return GraphTraversal(result)

    # ── Edge navigation ────────────────────────────────────────────────────────

    def out_e(self, *labels: str) -> "GraphTraversal":
        result = []
        for v in self._pipeline:
            result.extend(v.out_edges(*labels))
        return GraphTraversal(result)

    def in_e(self, *labels: str) -> "GraphTraversal":
        result = []
        for v in self._pipeline:
            result.extend(v.in_edges(*labels))
        return GraphTraversal(result)

    def both_e(self, *labels: str) -> "GraphTraversal":
        result = []
        for v in self._pipeline:
            result.extend(v.both_edges(*labels))
        return GraphTraversal(result)

    def out_v(self) -> "GraphTraversal":
        return GraphTraversal(e.out_vertex for e in self._pipeline)

    def in_v(self) -> "GraphTraversal":
        return GraphTraversal(e.in_vertex for e in self._pipeline)

    # ── Projection ─────────────────────────────────────────────────────────────

    def values(self, *keys: str) -> "GraphTraversal":
        result = []
        for e in self._pipeline:
            for k in keys:
                v = e.value(k)
                if v is not None:
                    result.append(v)
        return GraphTraversal(result)

    def id(self) -> "GraphTraversal":
        return GraphTraversal(e.id for e in self._pipeline)

    def label(self) -> "GraphTraversal":
        return GraphTraversal(e.label for e in self._pipeline)

    # ── Range / limiting ───────────────────────────────────────────────────────

    def dedup(self) -> "GraphTraversal":
        seen: set = set()
        unique = []
        for item in self._pipeline:
            key = getattr(item, "id", id(item))
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return GraphTraversal(unique)

    def limit(self, n: int) -> "GraphTraversal":
        return GraphTraversal(self._pipeline[:n])

    def skip(self, n: int) -> "GraphTraversal":
        return GraphTraversal(self._pipeline[n:])

    def range(self, low: int, high: int) -> "GraphTraversal":
        return GraphTraversal(self._pipeline[low:high])

    def tail(self, n: int = 1) -> "GraphTraversal":
        return GraphTraversal(self._pipeline[-n:])

    # ── Type conversion (TinkerPop 3.8.0) ─────────────────────────────────────

    def as_bool(self) -> "GraphTraversal":
        def convert(v):
            if isinstance(v, bool):
                return v
            if isinstance(v, str):
                return v.lower() == "true" or v == "1"
            if isinstance(v, (int, float)):
                return v != 0
            if v is None:
                raise ValueError("Can't parse null as Boolean.")
            raise TypeError(f"Cannot convert {v!r} to Boolean")
        return GraphTraversal(convert(v) for v in self._pipeline)

    def as_number(self) -> "GraphTraversal":
        def convert(v):
            if isinstance(v, bool):
                return 1 if v else 0
            if isinstance(v, (int, float)):
                return v
            if isinstance(v, str):
                try:
                    return int(v)
                except ValueError:
                    try:
                        return float(v)
                    except ValueError:
                        raise ValueError(f"Cannot parse '{v}' as a number")
            if v is None:
                raise ValueError("Can't parse null as Number.")
            raise TypeError(f"Cannot convert {v!r} to Number")
        return GraphTraversal(convert(v) for v in self._pipeline)

    # ── Collection steps (TinkerPop 3.8.0) ────────────────────────────────────

    def all(self, predicate) -> "GraphTraversal":
        def check(v):
            if isinstance(v, (list, tuple, set, frozenset)):
                return _builtins.all(predicate.test(x) for x in v)
            return predicate.test(v)
        return GraphTraversal(v for v in self._pipeline if check(v))

    def any(self, predicate) -> "GraphTraversal":
        def check(v):
            if isinstance(v, (list, tuple, set, frozenset)):
                return _builtins.any(predicate.test(x) for x in v)
            return predicate.test(v)
        return GraphTraversal(v for v in self._pipeline if check(v))

    def difference(self, values) -> "GraphTraversal":
        raise NotImplementedError("difference() step not yet implemented")

    def disjunct(self, values) -> "GraphTraversal":
        raise NotImplementedError("disjunct() step not yet implemented")

    def intersect(self, values) -> "GraphTraversal":
        raise NotImplementedError("intersect() step not yet implemented")

    def conjoin(self, delimiter: str) -> "GraphTraversal":
        raise NotImplementedError("conjoin() step not yet implemented")

    def combine(self, values) -> "GraphTraversal":
        raise NotImplementedError("combine() step not yet implemented")

    def product(self, values) -> "GraphTraversal":
        raise NotImplementedError("product() step not yet implemented")

    def merge(self, values) -> "GraphTraversal":
        raise NotImplementedError("merge() step not yet implemented")

    # ── Terminal ───────────────────────────────────────────────────────────────

    def to_list(self) -> List:
        return list(self._pipeline)

    def to_set(self) -> Set:
        return set(self._pipeline)

    def next(self) -> Optional[Any]:
        return self._pipeline[0] if self._pipeline else None

    def try_next(self) -> Optional[Any]:
        return self._pipeline[0] if self._pipeline else None

    def has_next(self) -> bool:
        return bool(self._pipeline)

    def count(self) -> "GraphTraversal":
        return GraphTraversal([len(self._pipeline)])

    def iterate(self) -> "GraphTraversal":
        self._pipeline = []
        return self


class GraphTraversalSource:
    """Entry point for traversals over a TinkerCat graph."""

    def __init__(self, graph: "TinkerCat"):
        self._graph = graph

    def V(self, *vertex_ids) -> GraphTraversal:
        """Start a traversal from all vertices, or from specific vertex IDs."""
        verts = self._graph.vertices()
        if vertex_ids:
            verts = [v for v in verts if v.id in vertex_ids]
        return GraphTraversal(verts)

    def E(self, *edge_ids) -> GraphTraversal:
        """Start a traversal from all edges, or from specific edge IDs."""
        edges = self._graph.edges()
        if edge_ids:
            edges = [e for e in edges if e.id in edge_ids]
        return GraphTraversal(edges)

    def add_v(self, label: str = "vertex", **properties) -> GraphTraversal:
        """Add a vertex and start a traversal from it."""
        v = self._graph.add_vertex(label, **properties)
        return GraphTraversal([v])
