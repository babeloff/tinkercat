"""
Tests for Task 2.1.1: Graph Traversal Iterators.

Verifies lazy iterator behaviour, direction/label filtering, and index-backed
property lookups.  See docs/project/changelog/task-2.1.1-graph-traversal-iterators.adoc.
"""

import pytest

from tinkercat import TinkerCat

from mocks import build_modern_graph

@pytest.fixture
def modern():
    with TinkerCat() as g:
        build_modern_graph(g)
        yield g

def test_vertices_returns_all_vertices(modern):
    assert sum(1 for _ in modern.vertices()) == 6

def test_edges_returns_all_edges(modern):
    assert sum(1 for _ in modern.edges()) == 6

def test_vertex_filter_by_label(modern):
    people = [v for v in modern.vertices() if v.label == "person"]
    assert len(people) == 4

def test_vertex_filter_by_property(modern):
    old = [v for v in modern.vertices() if (v.value("age") or 0) > 30]
    assert len(old) == 2  # josh(32), peter(35)

def test_out_edges_direction_filtering(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    out = list(marko.out_edges())
    assert len(out) == 3

def test_out_edges_label_filtering(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    knows = list(marko.out_edges("knows"))
    assert len(knows) == 2

def test_in_edges_direction_filtering(modern):
    lop = next(v for v in modern.vertices() if v.value("name") == "lop")
    in_edges = list(lop.in_edges())
    assert len(in_edges) == 3

def test_out_vertices_navigation(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    neighbors = list(marko.out_vertices("knows"))
    names = {v.value("name") for v in neighbors}
    assert names == {"vadas", "josh"}

def test_iterator_is_reusable_from_graph(modern):
    first  = sum(1 for _ in modern.vertices())
    second = sum(1 for _ in modern.vertices())
    assert first == second

def test_property_value_retrieval(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    assert marko.value("age") == 29

def test_edge_property_retrieval(modern):
    marko = next(v for v in modern.vertices() if v.value("name") == "marko")
    knows_edges = list(marko.out_edges("knows"))
    weights = {e.value("weight") for e in knows_edges}
    assert weights == {0.5, 1.0}
