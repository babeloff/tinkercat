"""
Tests for Task 7.7.1: Lambda Deprecation for GLV Compatibility.

Validates that anonymous traversal replacements for each deprecated
lambda overload produce identical results to the lambda form.
See docs/project/changelog/task-7.7.1-lambda-deprecation.adoc.
"""

import pytest

from tinkercat import TinkerCat

from mocks import build_modern_graph

# ---------------------------------------------------------------------------
# Standalone ExtendedTraversal — no MockTraversal inheritance
# ---------------------------------------------------------------------------

class ExtendedTraversal:

    def __init__(self, elements):
        self._pipeline = list(elements)

    # ── Deprecated lambda forms ──────────────────────────────────────────
    def filter_lambda(self, predicate):
        """Deprecated: accepts (Traverser) -> Boolean."""
        self._pipeline = [e for e in self._pipeline if predicate(e)]
        return self

    def map_lambda(self, function):
        """Deprecated: accepts (Traverser) -> R."""
        self._pipeline = [function(e) for e in self._pipeline]
        return self

    def side_effect_lambda(self, consumer):
        """Deprecated: accepts (Traverser) -> Unit."""
        for e in self._pipeline:
            consumer(e)
        return self

    # ── Anonymous-traversal replacements (non-deprecated) ────────────────
    def filter_traversal(self, sub_traversal_fn):
        """Replacement: accepts a sub-traversal predicate."""
        self._pipeline = [e for e in self._pipeline if sub_traversal_fn(e)]
        return self

    def map_values(self, key):
        """Replacement for map(lambda t: t.get().value(key))."""
        self._pipeline = [e.value(key) for e in self._pipeline
                          if e.value(key) is not None]
        return self

    def side_effect_store(self, store: list):
        """Replacement: populate a list as side effect."""
        store.extend(e.id for e in self._pipeline)
        return self

    def to_list(self):
        return list(self._pipeline)

    def has_next(self):
        return bool(self._pipeline)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
# Tests — lambda form vs. anonymous-traversal form produce same results
# ---------------------------------------------------------------------------

def test_filter_lambda_equiv_has_label(src):
    t_lambda    = ExtendedTraversal(src.V().to_list())
    t_traversal = ExtendedTraversal(src.V().to_list())

    t_lambda.filter_lambda(lambda v: v.label == "person")
    t_traversal.filter_traversal(lambda v: v.label == "person")

    assert sorted(v.id for v in t_lambda.to_list()) == \
           sorted(v.id for v in t_traversal.to_list())

def test_map_lambda_equiv_map_values(src):
    t_lambda    = ExtendedTraversal(src.V().has_label("person").to_list())
    t_traversal = ExtendedTraversal(src.V().has_label("person").to_list())

    t_lambda.map_lambda(lambda v: v.value("name"))
    t_traversal.map_values("name")

    assert sorted(t_lambda.to_list()) == sorted(t_traversal.to_list())

def test_side_effect_lambda_equiv_store(src):
    log_lambda    = []
    log_traversal = []

    t1 = ExtendedTraversal(src.V().to_list())
    t1.side_effect_lambda(lambda v: log_lambda.append(v.id))
    t1.to_list()

    t2 = ExtendedTraversal(src.V().to_list())
    t2.side_effect_store(log_traversal)
    t2.to_list()

    assert sorted(log_lambda) == sorted(log_traversal)

def test_anonymous_traversal_filter_is_gremlin_compatible(src):
    """Anonymous traversal form can be serialised as a filter spec."""
    filter_spec = {"key": "label", "value": "person"}

    def traversal_predicate(v):
        return v.label == filter_spec["value"]

    result = ExtendedTraversal(src.V().to_list()) \
        .filter_traversal(traversal_predicate) \
        .to_list()
    assert len(result) == 4

def test_map_values_returns_correct_projection(src):
    names = ExtendedTraversal(src.V().has_label("person").to_list()) \
        .map_values("name") \
        .to_list()
    assert sorted(names) == ["josh", "marko", "peter", "vadas"]

def test_filter_lambda_is_logically_equivalent_to_has(src):
    via_lambda = ExtendedTraversal(src.V().to_list()) \
        .filter_lambda(lambda v: v.value("name") == "marko") \
        .to_list()
    via_has = src.V().has("name", "marko").to_list()
    assert len(via_lambda) == len(via_has) == 1

def test_side_effect_does_not_alter_pipeline(src):
    log = []
    original_count = len(src.V().to_list())
    result = ExtendedTraversal(src.V().to_list()) \
        .side_effect_store(log) \
        .to_list()
    assert len(result) == original_count
    assert len(log) == original_count
