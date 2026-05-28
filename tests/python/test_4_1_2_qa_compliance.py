"""
Tests for Task 4.1.2: TinkerPop Compliance.

Python-side compliance checks mirroring the Structure and Process API
requirements from the Apache TinkerPop specification.
See docs/project/changelog/task-4.1.2-qa-compliance.adoc.
"""

import pytest

from tinkercat import TinkerCat

from mocks import build_modern_graph

@pytest.fixture
def modern():
    with TinkerCat() as g:
        build_modern_graph(g)
        yield g

# ── Structure API compliance ───────────────────────────────────────────────

def test_graph_has_vertices_method():
    with TinkerCat() as g:
        assert callable(getattr(g, "vertices", None))

def test_graph_has_edges_method():
    with TinkerCat() as g:
        assert callable(getattr(g, "edges", None))

def test_graph_has_add_vertex_method():
    with TinkerCat() as g:
        assert callable(getattr(g, "add_vertex", None))

def test_graph_has_add_edge_method():
    with TinkerCat() as g:
        assert callable(getattr(g, "add_edge", None))

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
        keys = list(v.properties.keys())
        assert isinstance(keys, list)

def test_values_iteration(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    vals = [marko.value(k) for k in ("name", "age")]
    assert "marko" in vals
    assert 29 in vals

# ── Feature advertisement compliance ──────────────────────────────────────

def test_vertex_count_property_exists():
    with TinkerCat() as g:
        assert hasattr(g, "vertex_count")

def test_edge_count_property_exists():
    with TinkerCat() as g:
        assert hasattr(g, "edge_count")

def test_context_manager_protocol():
    with TinkerCat() as g:
        g.add_vertex("node")
        assert g.vertex_count == 1
