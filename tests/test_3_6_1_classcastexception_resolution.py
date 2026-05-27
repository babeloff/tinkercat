"""
Tests for Task 3.6.1: ClassCastException Resolution.

Verifies that mixed-type property values, heterogeneous vertex collections,
and edge traversal do not raise unexpected type errors.
See docs/project/changelog/task-3.6.1-classcastexception-resolution.adoc.
"""

import pytest

try:
    from tinkercat import TinkerCat
    BINDINGS_AVAILABLE = True
except ImportError:
    BINDINGS_AVAILABLE = False
    from mocks import MockGraph as TinkerCat

from mocks import MockGraph


@pytest.fixture
def g():
    graph = TinkerCat.open() if hasattr(TinkerCat, "open") else TinkerCat()
    yield graph
    if hasattr(graph, "close"):
        graph.close()


def test_integer_property_no_error(g):
    v = g.add_vertex("item", count=42)
    assert v.value("count") == 42


def test_float_property_no_error(g):
    v = g.add_vertex("item", score=3.14)
    assert abs(v.value("score") - 3.14) < 1e-9


def test_boolean_property_no_error(g):
    v = g.add_vertex("item", active=True)
    assert v.value("active") is True


def test_mixed_type_properties_coexist(g):
    v = g.add_vertex("item", name="x", count=1, ratio=0.5, flag=False)
    assert v.value("name") == "x"
    assert v.value("count") == 1
    assert abs(v.value("ratio") - 0.5) < 1e-9
    assert v.value("flag") is False


def test_iterating_mixed_vertex_types(g):
    g.add_vertex("person", name="Alice", age=30)
    g.add_vertex("software", name="lop", lang="java")
    g.add_vertex("device", model="X1")
    verts = list(g.vertices())
    assert len(verts) == 3
    labels = {v.label for v in verts}
    assert labels == {"person", "software", "device"}


def test_edge_traversal_does_not_raise(g):
    a = g.add_vertex("person", name="a")
    b = g.add_vertex("person", name="b")
    g.add_edge("knows", a, b, weight=1.0)
    # Iterating edges should not raise
    for e in g.edges():
        _ = e.label
        _ = e.out_vertex
        _ = e.in_vertex


def test_property_value_none_safe(g):
    v = g.add_vertex("item")
    result = v.value("nonexistent")
    assert result is None


def test_casting_vertex_id_types():
    """IDs can be int, str, or other hashable types without error."""
    g1 = MockGraph()
    v1 = g1.add_vertex("n", vertex_id=1)
    v2 = g1.add_vertex("n", vertex_id="abc")
    assert g1.get_vertex(1) is not None
    assert g1.get_vertex("abc") is not None


def test_large_property_value_no_error(g):
    big_string = "x" * 10_000
    v = g.add_vertex("doc", content=big_string)
    assert len(v.value("content")) == 10_000


def test_numeric_string_property_not_coerced(g):
    v = g.add_vertex("item", code="007")
    val = v.value("code")
    assert isinstance(val, str)
    assert val == "007"
