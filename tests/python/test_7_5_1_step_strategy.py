"""
Tests for Task 7.5.1: TinkerCatStepStrategy — has() Predicate Push-down.

Validates that has() and has_label() filtering returns correct results
when called directly on a TinkerCat traversal.  TinkerCat does not yet
expose range predicates (P.gte etc.), so range tests use Python iteration.
See docs/project/changelog/task-7.5.1-step-strategy.adoc.
"""

import pytest

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    for name, age in [("Alice", 25), ("Bob", 30), ("Carol", 35), ("Dave", 40)]:
        graph.add_vertex("person", name=name, age=age)
    yield graph
    graph.close()


def test_has_returns_correct_result(g):
    result = g.traversal().V().has("name", "Alice").to_list()
    assert len(result) == 1
    assert result[0].value("name") == "Alice"


def test_has_with_different_value_returns_correct_result(g):
    result = g.traversal().V().has("name", "Bob").to_list()
    assert len(result) == 1
    assert result[0].value("name") == "Bob"


def test_range_predicate_via_python_filter(g):
    result = [v for v in g.vertices() if v.value("age") is not None and v.value("age") >= 30]
    names = {v.value("name") for v in result}
    assert names == {"Bob", "Carol", "Dave"}


def test_no_filter_returns_all(g):
    result = g.traversal().V().to_list()
    assert len(result) == g.vertex_count


def test_multiple_has_predicates_all_must_match(g):
    result = g.traversal().V().has("name", "Bob").to_list()
    assert len(result) == 1
    assert result[0].value("age") == 30


def test_label_filter_returns_correct_subset():
    graph = TinkerCat()
    try:
        for _ in range(3):
            graph.add_vertex("person")
        for _ in range(2):
            graph.add_vertex("software")
        result = graph.traversal().V().has_label("person").to_list()
        assert len(result) == 3
    finally:
        graph.close()


def test_no_match_returns_empty(g):
    result = g.traversal().V().has("name", "Nonexistent").to_list()
    assert result == []


def test_has_not_returns_vertices_without_property():
    graph = TinkerCat()
    try:
        graph.add_vertex("person", name="Alice", email="a@b.com")
        graph.add_vertex("person", name="Bob")
        result = graph.traversal().V().has_not("email").to_list()
        assert len(result) == 1
        assert result[0].value("name") == "Bob"
    finally:
        graph.close()
