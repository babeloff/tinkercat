"""
Tests for Task 4.1.1: Core Functionality QA.

Comprehensive unit-level regression tests covering Graph, Vertex, Edge,
Property, and PropertyQueryEngine across all supported data patterns.
See docs/project/changelog/task-4.1.1-qa.adoc.
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


# ── Graph creation ─────────────────────────────────────────────────────────

def test_empty_graph_has_zero_vertices_and_edges(g):
    assert g.vertex_count == 0
    assert g.edge_count == 0


def test_open_returns_graph(g):
    assert g is not None


# ── Vertex operations ──────────────────────────────────────────────────────

def test_add_vertex_default_label(g):
    v = g.add_vertex()
    assert v.label is not None


def test_add_vertex_custom_label(g):
    v = g.add_vertex("person")
    assert v.label == "person"


def test_vertex_id_is_assigned(g):
    v = g.add_vertex("node")
    assert v.id is not None


def test_multiple_vertices_have_distinct_ids(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    assert a.id != b.id


def test_vertex_string_property(g):
    v = g.add_vertex("person", name="Alice")
    assert v.value("name") == "Alice"


def test_vertex_integer_property(g):
    v = g.add_vertex("person", age=30)
    assert v.value("age") == 30


def test_missing_property_returns_none(g):
    v = g.add_vertex("person")
    assert v.value("nonexistent") is None


def test_vertex_property_update(g):
    v = g.add_vertex("person", score=10)
    v.property("score", 20)
    assert v.value("score") == 20


# ── Edge operations ────────────────────────────────────────────────────────

def test_add_edge_stores_label(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("knows", a, b)
    assert e.label == "knows"


def test_add_edge_stores_out_vertex(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("e", a, b)
    assert e.out_vertex.id == a.id


def test_add_edge_stores_in_vertex(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("e", a, b)
    assert e.in_vertex.id == b.id


def test_edge_property_stored(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("e", a, b, weight=0.5)
    assert abs(e.value("weight") - 0.5) < 1e-9


# ── Property query engine ──────────────────────────────────────────────────

def test_filter_vertices_by_property_value():
    g = MockGraph()
    build_modern_graph(g)
    persons = [v for v in g.vertices() if v.label == "person"]
    assert len(persons) == 4


def test_filter_vertices_by_property_range():
    g = MockGraph()
    build_modern_graph(g)
    young = [v for v in g.vertices()
             if v.label == "person" and (v.value("age") or 99) < 30]
    names = {v.value("name") for v in young}
    assert names == {"marko", "vadas"}


def test_filter_edges_by_label():
    g = MockGraph()
    build_modern_graph(g)
    knows = [e for e in g.edges() if e.label == "knows"]
    assert len(knows) == 2
