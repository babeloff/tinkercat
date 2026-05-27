"""
Lightweight mock objects used when TinkerCat Python bindings are not available.

All mock classes implement the same interface as their real counterparts so
test files can be written once and run against both implementations.
"""

from __future__ import annotations
from typing import Any, Dict, Iterator, List, Optional


class MockProperty:
    def __init__(self, key: str, value: Any):
        self._key = key
        self._value = value

    def key(self) -> str:
        return self._key

    def value(self) -> Any:
        return self._value

    def is_present(self) -> bool:
        return self._value is not None

    def __repr__(self) -> str:
        return f"MockProperty({self._key!r}={self._value!r})"


class MockVertex:
    def __init__(self, vertex_id: Any, label: str = "vertex"):
        self.id = vertex_id
        self.label = label
        self._properties: Dict[str, Any] = {}
        self._out_edges: List["MockEdge"] = []
        self._in_edges: List["MockEdge"] = []

    def property(self, key: str, value: Any = None, *meta) -> Any:
        if value is None:
            return MockProperty(key, self._properties.get(key))
        self._properties[key] = value
        return self

    def value(self, key: str) -> Any:
        return self._properties.get(key)

    def values(self, *keys: str) -> Iterator[Any]:
        if not keys:
            return iter(self._properties.values())
        return iter(self._properties[k] for k in keys if k in self._properties)

    def keys(self) -> Iterator[str]:
        return iter(self._properties.keys())

    def properties(self, *keys: str) -> Iterator[MockProperty]:
        ks = keys if keys else tuple(self._properties.keys())
        return iter(MockProperty(k, self._properties[k]) for k in ks if k in self._properties)

    def out_edges(self, *labels: str) -> Iterator["MockEdge"]:
        return iter(e for e in self._out_edges if not labels or e.label in labels)

    def in_edges(self, *labels: str) -> Iterator["MockEdge"]:
        return iter(e for e in self._in_edges if not labels or e.label in labels)

    def out_vertices(self, *labels: str) -> Iterator["MockVertex"]:
        return iter(e.in_vertex for e in self.out_edges(*labels))

    def in_vertices(self, *labels: str) -> Iterator["MockVertex"]:
        return iter(e.out_vertex for e in self.in_edges(*labels))

    def both_edges(self, *labels: str) -> Iterator["MockEdge"]:
        return iter(list(self.out_edges(*labels)) + list(self.in_edges(*labels)))

    def both_vertices(self, *labels: str) -> Iterator["MockVertex"]:
        return iter(list(self.out_vertices(*labels)) + list(self.in_vertices(*labels)))

    def __repr__(self) -> str:
        return f"v[{self.id}:{self.label}]"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MockVertex) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class MockEdge:
    def __init__(self, edge_id: Any, label: str, out_vertex: MockVertex, in_vertex: MockVertex):
        self.id = edge_id
        self.label = label
        self.out_vertex = out_vertex
        self.in_vertex = in_vertex
        self._properties: Dict[str, Any] = {}

    def property(self, key: str, value: Any = None) -> Any:
        if value is None:
            return MockProperty(key, self._properties.get(key))
        self._properties[key] = value
        return self

    def value(self, key: str) -> Any:
        return self._properties.get(key)

    def properties(self, *keys: str) -> Iterator[MockProperty]:
        ks = keys if keys else tuple(self._properties.keys())
        return iter(MockProperty(k, self._properties[k]) for k in ks if k in self._properties)

    def __repr__(self) -> str:
        return f"e[{self.id}:{self.label}]"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MockEdge) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


class MockGraph:
    """Mock TinkerCat graph matching the real Python binding API."""

    def __init__(self, allow_null_properties: bool = False):
        self._vertices: Dict[Any, MockVertex] = {}
        self._edges: Dict[Any, MockEdge] = {}
        self._next_id: int = 1
        self.allow_null_properties = allow_null_properties

    @classmethod
    def open(cls, config: Optional[Dict[str, Any]] = None) -> "MockGraph":
        config = config or {}
        return cls(allow_null_properties=config.get("allowNullPropertyValues", False))

    def add_vertex(self, label: str = "vertex", vertex_id: Any = None, **properties) -> MockVertex:
        vid = vertex_id if vertex_id is not None else self._next_id
        try:
            self._next_id = max(int(vid), self._next_id) + 1
        except (ValueError, TypeError):
            self._next_id += 1
        v = MockVertex(vid, label)
        for k, val in properties.items():
            v.property(k, val)
        self._vertices[vid] = v
        return v

    def add_edge(self, label: str, out_vertex: MockVertex, in_vertex: MockVertex,
                 **properties) -> MockEdge:
        eid = self._next_id
        self._next_id += 1
        e = MockEdge(eid, label, out_vertex, in_vertex)
        for k, v in properties.items():
            e._properties[k] = v
        self._edges[eid] = e
        out_vertex._out_edges.append(e)
        in_vertex._in_edges.append(e)
        return e

    def vertices(self, **filters) -> Iterator[MockVertex]:
        result = list(self._vertices.values())
        if "label" in filters:
            result = [v for v in result if v.label == filters.pop("label")]
        for k, val in filters.items():
            result = [v for v in result if v._properties.get(k) == val]
        return iter(result)

    def edges(self, **filters) -> Iterator[MockEdge]:
        result = list(self._edges.values())
        for k, val in filters.items():
            result = [e for e in result if e._properties.get(k) == val]
        return iter(result)

    def get_vertex(self, vertex_id: Any) -> Optional[MockVertex]:
        return self._vertices.get(vertex_id)

    @property
    def vertex_count(self) -> int:
        return len(self._vertices)

    @property
    def edge_count(self) -> int:
        return len(self._edges)

    def __len__(self) -> int:
        return self.vertex_count

    def close(self) -> None:
        pass

    def __enter__(self) -> "MockGraph":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"MockGraph(vertices={self.vertex_count}, edges={self.edge_count})"


# ---------------------------------------------------------------------------
# Utility: build the "modern" TinkerPop toy graph using whichever graph class
# is passed in.  Used by multiple test modules.
# ---------------------------------------------------------------------------

def build_modern_graph(graph):
    """Populate *graph* with the standard TinkerPop modern toy graph."""
    marko   = graph.add_vertex("person", name="marko",  age=29)
    vadas   = graph.add_vertex("person", name="vadas",  age=27)
    lop     = graph.add_vertex("software", name="lop",  lang="java")
    josh    = graph.add_vertex("person", name="josh",   age=32)
    ripple  = graph.add_vertex("software", name="ripple", lang="java")
    peter   = graph.add_vertex("person", name="peter",  age=35)

    graph.add_edge("knows",   marko, vadas, weight=0.5)
    graph.add_edge("knows",   marko, josh,  weight=1.0)
    graph.add_edge("created", marko, lop,   weight=0.4)
    graph.add_edge("created", josh,  ripple, weight=1.0)
    graph.add_edge("created", josh,  lop,   weight=0.4)
    graph.add_edge("created", peter, lop,   weight=0.2)

    return marko, vadas, lop, josh, ripple, peter
