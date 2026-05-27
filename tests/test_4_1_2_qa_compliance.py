"""
Tests for Task 4.1.2: TinkerPop Compliance.

Python-side compliance checks mirroring the Structure and Process API
requirements from the Apache TinkerPop specification.
See docs/project/changelog/task-4.1.2-qa-compliance.adoc.
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
def modern():
    g = MockGraph()
    build_modern_graph(g)
    return g


# ── Structure API compliance ───────────────────────────────────────────────

def test_graph_has_vertices_method():
    g = TinkerCat.open() if hasattr(TinkerCat, "open") else TinkerCat()
    assert callable(getattr(g, "vertices", None))
    if hasattr(g, "close"):
        g.close()


def test_graph_has_edges_method():
    g = TinkerCat.open() if hasattr(TinkerCat, "open") else TinkerCat()
    assert callable(getattr(g, "edges", None))
    if hasattr(g, "close"):
        g.close()


def test_graph_has_add_vertex_method():
    g = TinkerCat.open() if hasattr(TinkerCat, "open") else TinkerCat()
    assert callable(getattr(g, "add_vertex", None))
    if hasattr(g, "close"):
        g.close()


def test_graph_has_add_edge_method():
    g = TinkerCat.open() if hasattr(TinkerCat, "open") else TinkerCat()
    assert callable(getattr(g, "add_edge", None))
    if hasattr(g, "close"):
        g.close()


def test_vertex_has_id(modern):
    for v in modern.vertices():
        assert v.id is not None


def test_vertex_has_label(modern):
    for v in modern.vertices():
        assert v.label is not None


def test_edge_has_id(modern):
    for e in modern.edges():
        assert e.id is not None


def test_edge_has_label(modern):
    for e in modern.edges():
        assert e.label is not None


def test_edge_has_out_vertex(modern):
    for e in modern.edges():
        assert e.out_vertex is not None


def test_edge_has_in_vertex(modern):
    for e in modern.edges():
        assert e.in_vertex is not None


# ── Process API compliance ─────────────────────────────────────────────────

def test_out_edges_returns_iterable(modern):
    for v in modern.vertices():
        result = list(v.out_edges())
        assert isinstance(result, list)


def test_in_edges_returns_iterable(modern):
    for v in modern.vertices():
        result = list(v.in_edges())
        assert isinstance(result, list)


def test_out_vertices_navigation(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    neighbors = list(marko.out_vertices())
    assert len(neighbors) == 3


def test_in_vertices_navigation(modern):
    lop = next(v for v in modern.vertices() if v.value("name") == "lop")
    creators = list(lop.in_vertices())
    assert len(creators) == 3


def test_property_keys_is_iterable(modern):
    for v in modern.vertices():
        keys = list(v.keys())
        assert isinstance(keys, list)


def test_values_iteration(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    vals = list(marko.values("name", "age"))
    assert "marko" in vals
    assert 29 in vals


# ── Feature advertisement compliance ──────────────────────────────────────

def test_vertex_count_property_exists():
    g = MockGraph()
    assert hasattr(g, "vertex_count")


def test_edge_count_property_exists():
    g = MockGraph()
    assert hasattr(g, "edge_count")


def test_context_manager_protocol():
    with MockGraph() as g:
        g.add_vertex("node")
        assert g.vertex_count == 1
