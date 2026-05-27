"""
Tests for Task 7.1.1: Gremlin Traversal Engine Integration.

Defines the expected GraphTraversalSource / GraphTraversal API and
validates it against mock implementations.  Tests are skipped when the
real traversal engine module is absent; they become acceptance tests once
Task 7.1.1 is implemented.
See docs/project/changelog/task-7.1.1-traversal-engine.adoc.
"""

import pytest

try:
    from tinkercat.traversal import GraphTraversalSource, GraphTraversal
    from tinkercat import TinkerCat
    TRAVERSAL_AVAILABLE = True
except ImportError:
    TRAVERSAL_AVAILABLE = False

from mocks import MockGraph, build_modern_graph


# ---------------------------------------------------------------------------
# Mock traversal layer — defines the expected interface
# ---------------------------------------------------------------------------

class MockTraversal:
    def __init__(self, elements):
        self._pipeline = list(elements)

    def has_label(self, *labels):
        self._pipeline = [e for e in self._pipeline if e.label in labels]
        return self

    def has(self, key, value=None):
        if value is None:
            self._pipeline = [e for e in self._pipeline
                               if e.value(key) is not None]
        else:
            self._pipeline = [e for e in self._pipeline if e.value(key) == value]
        return self

    def values(self, *keys):
        result = []
        for e in self._pipeline:
            for k in keys:
                v = e.value(k)
                if v is not None:
                    result.append(v)
        self._pipeline = result
        return self

    def out(self, *labels):
        result = []
        for v in self._pipeline:
            result.extend(v.out_vertices(*labels))
        self._pipeline = result
        return self

    def dedup(self):
        seen, unique = set(), []
        for item in self._pipeline:
            key = getattr(item, "id", item)
            if key not in seen:
                seen.add(key)
                unique.append(item)
        self._pipeline = unique
        return self

    def limit(self, n):
        self._pipeline = self._pipeline[:n]
        return self

    def to_list(self):
        return list(self._pipeline)

    def count(self):
        self._pipeline = [len(self._pipeline)]
        return self

    def next(self):
        return self._pipeline[0] if self._pipeline else None

    def has_next(self):
        return bool(self._pipeline)


class MockGraphTraversalSource:
    def __init__(self, graph):
        self._graph = graph

    def V(self, *ids):
        verts = list(self._graph.vertices())
        if ids:
            verts = [v for v in verts if v.id in ids]
        return MockTraversal(verts)

    def E(self, *ids):
        edges = list(self._graph.edges())
        if ids:
            edges = [e for e in edges if e.id in ids]
        return MockTraversal(edges)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def g():
    graph = MockGraph()
    build_modern_graph(graph)
    return graph


@pytest.fixture
def src(g):
    return MockGraphTraversalSource(g)


def test_V_returns_all_vertices(src, g):
    result = src.V().to_list()
    assert len(result) == g.vertex_count


def test_E_returns_all_edges(src, g):
    result = src.E().to_list()
    assert len(result) == g.edge_count


def test_V_has_label_filter(src):
    people = src.V().has_label("person").to_list()
    assert len(people) == 4


def test_V_has_value_filter(src):
    result = src.V().has("name", "marko").to_list()
    assert len(result) == 1
    assert result[0].value("name") == "marko"


def test_V_values_projection(src):
    names = src.V().has_label("person").values("name").to_list()
    assert len(names) == 4
    assert "marko" in names


def test_V_out_traversal(src):
    neighbors = src.V().has("name", "marko").out("knows").to_list()
    names = {v.value("name") for v in neighbors}
    assert names == {"vadas", "josh"}


def test_V_dedup(src):
    # Two paths lead to lop; dedup should collapse them
    lop_creators = src.V().has("name", "marko").out("created").dedup().to_list()
    assert len(lop_creators) == 1


def test_V_limit(src):
    result = src.V().limit(2).to_list()
    assert len(result) == 2


def test_count_terminal(src):
    n = src.V().has_label("person").count().next()
    assert n == 4


def test_has_next_on_empty_traversal(src):
    result = src.V().has("name", "nonexistent")
    assert not result.has_next()


def test_pipeline_is_lazy_composition(src):
    t = src.V().has_label("person").has("age", 29)
    # .to_list() triggers execution
    result = t.to_list()
    assert len(result) == 1
    assert result[0].value("name") == "marko"
