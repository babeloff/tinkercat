"""
Tests for Task 4.0.1: Kotest Migration.

Python-side regression tests that validate the core API surface covered
by the Kotest StringSpec migration.  Structural mirrors of the Kotlin
test suite executed here via the Python binding / mock.
See docs/project/changelog/task-4.0.1-kotest-migration.adoc.
"""

import pytest

try:
    from tinkercat import TinkerCat, Vertex, Edge
    BINDINGS_AVAILABLE = True
except ImportError:
    BINDINGS_AVAILABLE = False
    from mocks import MockGraph as TinkerCat, MockVertex as Vertex, MockEdge as Edge

from mocks import MockGraph, build_modern_graph


@pytest.fixture
def g():
    graph = TinkerCat.open() if hasattr(TinkerCat, "open") else TinkerCat()
    yield graph
    if hasattr(graph, "close"):
        graph.close()


# ── Structure API ──────────────────────────────────────────────────────────

def test_add_vertex_increments_count(g):
    assert g.vertex_count == 0
    g.add_vertex("node")
    assert g.vertex_count == 1


def test_add_edge_increments_count(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    assert g.edge_count == 0
    g.add_edge("e", a, b)
    assert g.edge_count == 1


def test_vertex_label_stored(g):
    v = g.add_vertex("person")
    assert v.label == "person"


def test_vertex_property_stored(g):
    v = g.add_vertex("person", name="Alice")
    assert v.value("name") == "Alice"


def test_edge_label_stored(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("knows", a, b)
    assert e.label == "knows"


def test_edge_out_vertex(g):
    a = g.add_vertex("n", name="a")
    b = g.add_vertex("n", name="b")
    e = g.add_edge("e", a, b)
    assert e.out_vertex.id == a.id


def test_edge_in_vertex(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("e", a, b)
    assert e.in_vertex.id == b.id


def test_vertices_iterator_yields_all(g):
    for _ in range(5):
        g.add_vertex("node")
    assert sum(1 for _ in g.vertices()) == 5


def test_edges_iterator_yields_all(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    c = g.add_vertex("n")
    g.add_edge("e", a, b)
    g.add_edge("e", b, c)
    assert sum(1 for _ in g.edges()) == 2


# ── Cross-platform consistency mirror ─────────────────────────────────────

def test_modern_graph_has_six_vertices():
    g = MockGraph()
    build_modern_graph(g)
    assert g.vertex_count == 6


def test_modern_graph_has_six_edges():
    g = MockGraph()
    build_modern_graph(g)
    assert g.edge_count == 6


def test_modern_graph_labels():
    g = MockGraph()
    build_modern_graph(g)
    labels = {v.label for v in g.vertices()}
    assert labels == {"person", "software"}
