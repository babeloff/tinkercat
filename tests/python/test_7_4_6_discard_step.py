"""
Tests for Task 7.4.6: discard() Step.

All tests call g.traversal().V().discard() on a live TinkerCat graph.
The discard() step is not yet implemented; every test fails with
AttributeError until it is added to GraphTraversal.
Note: iterate() IS implemented and is used as a comparison baseline.
See docs/project/changelog/task-7.4.6-discard-step.adoc.
"""

import pytest

from tinkercat import TinkerCat
from mocks import build_modern_graph


@pytest.fixture
def g():
    graph = TinkerCat()
    build_modern_graph(graph)
    yield graph
    graph.close()


def test_discard_returns_none(g):
    result = g.traversal().V().discard()  # AttributeError until implemented
    assert result is None


def test_discard_on_empty_traversal_no_error():
    graph = TinkerCat()
    try:
        result = graph.traversal().V().discard()  # AttributeError until implemented
        assert result is None
    finally:
        graph.close()


def test_discard_drains_pipeline(g):
    t = g.traversal().V()
    t.discard()  # AttributeError until implemented
    assert t.to_list() == []


def test_side_effects_execute_before_discard(g):
    log = []
    g.traversal().V().side_effect(lambda v: log.append(v.id)).discard()  # AttributeError
    assert len(log) == g.vertex_count


def test_property_mutation_applied_before_discard(g):
    g.traversal().V().property("migrated", True).discard()  # AttributeError
    for v in g.vertices():
        assert v.value("migrated") is True


def test_discard_vs_iterate_same_side_effects(g):
    log_discard = []
    log_iterate = []

    g.traversal().V().side_effect(lambda v: log_discard.append(v.id)).discard()  # AttributeError
    g.traversal().V().side_effect(lambda v: log_iterate.append(v.id)).iterate()

    assert sorted(log_discard) == sorted(log_iterate)
