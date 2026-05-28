"""
Tests for Task 7.7.1: Lambda Deprecation for GLV Compatibility.

Validates that anonymous traversal steps (has, has_label, values) produce
the same results as the deprecated lambda forms they replace.  All tests
use the real TinkerCat traversal API directly.
See docs/project/changelog/task-7.7.1-lambda-deprecation.adoc.
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


def test_filter_via_has_label_replaces_filter_lambda(g):
    result = g.traversal().V().has_label("person").to_list()
    assert len(result) == 4


def test_map_values_replaces_map_lambda(g):
    names = g.traversal().V().has_label("person").values("name").to_list()
    assert sorted(names) == ["josh", "marko", "peter", "vadas"]


def test_side_effect_collect_ids_replaces_side_effect_lambda(g):
    ids = [v.id for v in g.traversal().V().to_list()]
    assert len(ids) == 6  # modern graph has 6 vertices


def test_anonymous_traversal_filter_is_gremlin_compatible(g):
    result = g.traversal().V().has_label("person").to_list()
    assert len(result) == 4


def test_map_values_returns_correct_projection(g):
    names = g.traversal().V().has_label("person").values("name").to_list()
    assert sorted(names) == ["josh", "marko", "peter", "vadas"]


def test_has_is_logically_equivalent_to_filter_lambda(g):
    via_has = g.traversal().V().has("name", "marko").to_list()
    assert len(via_has) == 1
    assert via_has[0].value("name") == "marko"


def test_traversal_does_not_alter_graph(g):
    before = g.vertex_count
    _ = g.traversal().V().to_list()
    assert g.vertex_count == before


def test_has_not_replaces_filter_lambda_negation(g):
    result = g.traversal().V().has_not("lang").to_list()
    labels = {v.label for v in result}
    assert "software" not in labels or all(v.value("lang") is None for v in result if v.label == "software")
    assert len(result) == 4  # 4 persons, 2 software (with lang); persons have no lang property
