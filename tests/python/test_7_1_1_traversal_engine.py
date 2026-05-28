"""
Tests for Task 7.1.1: Gremlin Traversal Engine Integration.

All tests run against the real TinkerCat graph via its Python bindings.
The suite is skipped automatically when the native library is not built
(run `pixi run python-native && pixi run python-setup` to enable it).
See docs/project/changelog/task-7.1.1-traversal-engine.adoc.
"""

import pytest

from tinkercat import TinkerCat
from tinkercat.traversal import GraphTraversalSource, GraphTraversal

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def build_modern_graph(graph: "TinkerCat"):
    """Populate *graph* with the standard TinkerPop modern toy graph."""
    marko  = graph.add_vertex("person",   name="marko",  age=29)
    vadas  = graph.add_vertex("person",   name="vadas",  age=27)
    lop    = graph.add_vertex("software", name="lop",    lang="java")
    josh   = graph.add_vertex("person",   name="josh",   age=32)
    ripple = graph.add_vertex("software", name="ripple", lang="java")
    peter  = graph.add_vertex("person",   name="peter",  age=35)

    graph.add_edge("knows",   marko, vadas,  weight=0.5)
    graph.add_edge("knows",   marko, josh,   weight=1.0)
    graph.add_edge("created", marko, lop,    weight=0.4)
    graph.add_edge("created", josh,  ripple, weight=1.0)
    graph.add_edge("created", josh,  lop,    weight=0.4)
    graph.add_edge("created", peter, lop,    weight=0.2)

    return marko, vadas, lop, josh, ripple, peter

@pytest.fixture
def g():
    graph = TinkerCat()
    build_modern_graph(graph)
    yield graph
    graph.close()

@pytest.fixture
def src(g):
    return g.traversal()

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

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
    lop_creators = src.V().has("name", "marko").out("created").dedup().to_list()
    assert len(lop_creators) == 1

def test_V_limit(src):
    result = src.V().limit(2).to_list()
    assert len(result) == 2

def test_count_terminal(src):
    n = src.V().has_label("person").count().next()
    assert n == 4

def test_has_next_on_empty_traversal(src):
    assert not src.V().has("name", "nonexistent").has_next()

def test_pipeline_composition(src):
    result = src.V().has_label("person").has("age", 29).to_list()
    assert len(result) == 1
    assert result[0].value("name") == "marko"

def test_V_by_id(src, g):
    first_id = src.V().to_list()[0].id
    result = src.V(first_id).to_list()
    assert len(result) == 1
    assert result[0].id == first_id

def test_in_traversal(src):
    result = src.V().has("name", "josh").in_("knows").to_list()
    names = {v.value("name") for v in result}
    assert "marko" in names

def test_out_e_traversal(src):
    edges = src.V().has("name", "marko").out_e("knows").to_list()
    assert len(edges) == 2

def test_in_v_from_edge(src):
    vertices = src.V().has("name", "marko").out_e("knows").in_v().to_list()
    names = {v.value("name") for v in vertices}
    assert names == {"vadas", "josh"}

def test_skip(src, g):
    skipped = src.V().skip(2).to_list()
    assert len(skipped) == g.vertex_count - 2

def test_range(src):
    result = src.V().range(1, 3).to_list()
    assert len(result) == 2

def test_tail(src):
    result = src.V().tail(2).to_list()
    assert len(result) == 2

def test_to_set(src):
    result = src.V().has_label("person").to_set()
    assert len(result) == 4

def test_try_next_on_empty(src):
    assert src.V().has("name", "nobody").try_next() is None

def test_iterate_drains_traversal(src):
    t = src.V().has_label("person")
    t.iterate()
    assert not t.has_next()

def test_traversal_source_type(g):
    assert isinstance(g.traversal(), GraphTraversalSource)

def test_traversal_type(g):
    assert isinstance(g.traversal().V(), GraphTraversal)
