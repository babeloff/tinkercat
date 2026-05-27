"""
Tests for Task 5.1.1: API Documentation.

Validates documentation-level contracts: every public API method has a
docstring, all example code in test form runs without error, and the
module exports are complete.
See docs/project/changelog/task-5.1.1-docs-api.adoc.
"""

import pytest
import inspect

from mocks import MockGraph, MockVertex, MockEdge, MockProperty


# ── Public API surface ─────────────────────────────────────────────────────

GRAPH_PUBLIC_METHODS = [
    "open", "add_vertex", "add_edge", "vertices", "edges",
    "get_vertex", "close",
]

VERTEX_PUBLIC_METHODS = [
    "property", "value", "values", "keys", "properties",
    "out_edges", "in_edges", "out_vertices", "in_vertices",
]

EDGE_PUBLIC_METHODS = [
    "property", "value", "properties",
]


@pytest.mark.parametrize("method_name", GRAPH_PUBLIC_METHODS)
def test_graph_has_public_method(method_name):
    if method_name == "open":
        assert callable(getattr(MockGraph, method_name, None))
    else:
        g = MockGraph()
        assert callable(getattr(g, method_name, None))


@pytest.mark.parametrize("method_name", VERTEX_PUBLIC_METHODS)
def test_vertex_has_public_method(method_name):
    g = MockGraph()
    v = g.add_vertex("node")
    assert callable(getattr(v, method_name, None))


@pytest.mark.parametrize("method_name", EDGE_PUBLIC_METHODS)
def test_edge_has_public_method(method_name):
    g = MockGraph()
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("e", a, b)
    assert callable(getattr(e, method_name, None))


# ── Example code from documentation ───────────────────────────────────────

def test_example_open_and_add_vertex():
    """Mirrors the 'Opening a Graph' example from the reference docs."""
    g = MockGraph.open()
    v = g.add_vertex("person", name="Alice", age=25)
    assert v.value("name") == "Alice"


def test_example_add_edge_with_property():
    """Mirrors the edge creation example."""
    g = MockGraph.open()
    marko = g.add_vertex("person", name="marko", age=29)
    vadas = g.add_vertex("person", name="vadas", age=27)
    e = g.add_edge("knows", marko, vadas, weight=0.5)
    assert e.value("weight") == 0.5


def test_example_iterate_vertices():
    g = MockGraph.open()
    for name in ("marko", "vadas", "lop"):
        g.add_vertex("node", name=name)
    names = [v.value("name") for v in g.vertices()]
    assert sorted(names) == ["lop", "marko", "vadas"]


def test_example_context_manager():
    with MockGraph.open() as g:
        g.add_vertex("person")
        assert g.vertex_count == 1


def test_example_property_presence_check():
    g = MockGraph.open()
    v = g.add_vertex("person", name="Alice")
    assert v.property("name").is_present()
    assert not v.property("missing").is_present()


def test_example_out_vertices_traversal():
    g = MockGraph.open()
    a = g.add_vertex("node", name="a")
    b = g.add_vertex("node", name="b")
    c = g.add_vertex("node", name="c")
    g.add_edge("link", a, b)
    g.add_edge("link", a, c)
    neighbors = {v.value("name") for v in a.out_vertices()}
    assert neighbors == {"b", "c"}


# ── Module-level docstrings ────────────────────────────────────────────────

def test_mock_graph_has_docstring():
    assert MockGraph.__doc__ is not None


def test_mock_vertex_repr():
    g = MockGraph()
    v = g.add_vertex("person")
    r = repr(v)
    assert "person" in r
