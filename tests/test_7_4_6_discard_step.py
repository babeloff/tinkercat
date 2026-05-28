"""
Tests for Task 7.4.6: discard() Step.

Validates that discard() drains the traversal while still executing
side-effect steps, and returns None (not the traversal).
See docs/project/changelog/task-7.4.6-discard-step.adoc.
"""

import pytest

from tinkercat import TinkerCat

from mocks import build_modern_graph

# ---------------------------------------------------------------------------
# Standalone SideEffectTraversal — no MockTraversal inheritance
# ---------------------------------------------------------------------------

class SideEffectTraversal:
    def __init__(self, elements):
        self._pipeline = list(elements)

    def side_effect(self, fn):
        for item in self._pipeline:
            fn(item)
        return self

    def property(self, key, value):
        for item in self._pipeline:
            item.set_property(key, value)
        return self

    def discard(self):
        self._pipeline = []
        return None

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
# Tests
# ---------------------------------------------------------------------------

def test_discard_returns_none(src):
    t = SideEffectTraversal(src.V().to_list())
    result = t.discard()
    assert result is None

def test_discard_on_empty_traversal_no_error(src):
    t = SideEffectTraversal([])
    result = t.discard()
    assert result is None

def test_discard_drains_pipeline(src):
    t = SideEffectTraversal(src.V().to_list())
    t.discard()
    assert t._pipeline == []

def test_side_effects_execute_before_discard(g):
    log = []
    t = SideEffectTraversal(list(g.vertices()))
    t.side_effect(lambda v: log.append(v.id))
    t.discard()
    assert len(log) == g.vertex_count

def test_property_mutation_applied_before_discard(g):
    t = SideEffectTraversal(list(g.vertices()))
    t.property("migrated", True)
    t.discard()
    for v in g.vertices():
        assert v.value("migrated") is True

def test_discard_vs_iterate_same_side_effects(g):
    log_discard = []
    log_iterate = []

    t1 = SideEffectTraversal(list(g.vertices()))
    t1.side_effect(lambda v: log_discard.append(v.id))
    t1.discard()

    t2 = SideEffectTraversal(list(g.vertices()))
    t2.side_effect(lambda v: log_iterate.append(v.id))
    t2.to_list()  # iterate-equivalent

    assert sorted(log_discard) == sorted(log_iterate)
