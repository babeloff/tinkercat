"""
Tests for Task 5.1.1: API Documentation.

Validates documentation-level contracts: every public API method exists,
all example code in test form runs without error, and the module exports
are complete.
See docs/project/changelog/task-5.1.1-docs-api.adoc.
"""

import pytest
import inspect

from tinkercat import TinkerCat

# ── Public API surface ─────────────────────────────────────────────────────

GRAPH_PUBLIC_METHODS = [
    "add_vertex", "add_edge", "vertices", "edges",
    "get_vertex", "close",
]

GRAPH_PUBLIC_PROPERTIES = [
    "vertex_count", "edge_count",
]

VERTEX_PUBLIC_METHODS = [
    "value", "get_property", "set_property",
    "out_edges", "in_edges", "out_vertices", "in_vertices",
]

VERTEX_PUBLIC_ATTRIBUTES = [
    "id", "label", "properties",
]

EDGE_PUBLIC_METHODS = [
    "value", "get_property", "set_property",
]

EDGE_PUBLIC_ATTRIBUTES = [
    "id", "label", "out_vertex", "in_vertex", "properties",
]

@pytest.mark.parametrize("method_name", GRAPH_PUBLIC_METHODS)
def test_graph_has_public_method(method_name):
    g = TinkerCat()
    assert callable(getattr(g, method_name, None))
    g.close()

@pytest.mark.parametrize("prop_name", GRAPH_PUBLIC_PROPERTIES)
def test_graph_has_public_property(prop_name):
    g = TinkerCat()
    # Properties are accessible as attributes
    assert hasattr(g, prop_name)
    g.close()

@pytest.mark.parametrize("method_name", VERTEX_PUBLIC_METHODS)
def test_vertex_has_public_method(method_name):
    g = TinkerCat()
    v = g.add_vertex("node")
    assert callable(getattr(v, method_name, None))
    g.close()

@pytest.mark.parametrize("attr_name", VERTEX_PUBLIC_ATTRIBUTES)
def test_vertex_has_public_attribute(attr_name):
    g = TinkerCat()
    v = g.add_vertex("node")
    assert hasattr(v, attr_name)
    g.close()

@pytest.mark.parametrize("method_name", EDGE_PUBLIC_METHODS)
def test_edge_has_public_method(method_name):
    g = TinkerCat()
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("e", a, b)
    assert callable(getattr(e, method_name, None))
    g.close()

@pytest.mark.parametrize("attr_name", EDGE_PUBLIC_ATTRIBUTES)
def test_edge_has_public_attribute(attr_name):
    g = TinkerCat()
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("e", a, b)
    assert hasattr(e, attr_name)
    g.close()

# ── Example code from documentation ───────────────────────────────────────

def test_example_open_and_add_vertex():
    """Mirrors the 'Opening a Graph' example from the reference docs."""
    g = TinkerCat()
    v = g.add_vertex("person", name="Alice", age=25)
    assert v.value("name") == "Alice"
    g.close()

def test_example_add_edge_with_property():
    """Mirrors the edge creation example."""
    g = TinkerCat()
    marko = g.add_vertex("person", name="marko", age=29)
    vadas = g.add_vertex("person", name="vadas", age=27)
    e = g.add_edge("knows", marko, vadas, weight=0.5)
    assert e.value("weight") == 0.5
    g.close()

def test_example_iterate_vertices():
    g = TinkerCat()
    for name in ("marko", "vadas", "lop"):
        g.add_vertex("node", name=name)
    names = [v.value("name") for v in g.vertices()]
    assert sorted(names) == ["lop", "marko", "vadas"]
    g.close()

def test_example_context_manager():
    with TinkerCat() as g:
        g.add_vertex("person")
        assert g.vertex_count == 1

def test_example_property_presence_check():
    g = TinkerCat()
    v = g.add_vertex("person", name="Alice")
    assert v.value("name") is not None
    assert v.value("missing") is None
    g.close()

def test_example_out_vertices_traversal():
    g = TinkerCat()
    a = g.add_vertex("node", name="a")
    b = g.add_vertex("node", name="b")
    c = g.add_vertex("node", name="c")
    g.add_edge("link", a, b)
    g.add_edge("link", a, c)
    neighbors = {v.value("name") for v in a.out_vertices()}
    assert neighbors == {"b", "c"}
    g.close()

# ── Class-level docstrings ─────────────────────────────────────────────────

def test_tinkercat_has_docstring():
    assert TinkerCat.__doc__ is not None

def test_vertex_repr():
    g = TinkerCat()
    v = g.add_vertex("person")
    r = repr(v)
    assert r is not None and len(r) > 0
    g.close()
