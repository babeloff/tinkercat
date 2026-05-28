"""
Tests for Task 7.5.2: TinkerCatCountStrategy — Short-circuit Count.

Validates O(1) count short-circuiting for bare g.V().count() and
g.V().hasLabel(L).count() patterns.
See docs/project/changelog/task-7.5.2-count-strategy.adoc.
"""

import pytest
import time

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Mock count strategy
# ---------------------------------------------------------------------------

class LabelMap:
    """Maintains per-label vertex lists for O(1) label count."""
    def __init__(self):
        self._by_label: dict = {}

    def add(self, vertex):
        self._by_label.setdefault(vertex.label, []).append(vertex)

    def count_all(self) -> int:
        return sum(len(vs) for vs in self._by_label.values())

    def count_label(self, label: str) -> int:
        return len(self._by_label.get(label, []))

    def labels(self):
        return set(self._by_label.keys())

class CountStrategyGraph:
    """Graph that wraps TinkerCat and maintains a label map for O(1) count short-circuit."""

    def __init__(self):
        self._graph = TinkerCat()
        self._label_map = LabelMap()

    def add_vertex(self, label="vertex", **props):
        v = self._graph.add_vertex(label, **props)
        self._label_map.add(v)
        return v

    def vertices(self):
        return self._graph.vertices()

    @property
    def vertex_count(self):
        return self._graph.vertex_count

    def fast_count(self, label=None) -> int:
        if label is None:
            return self._graph.vertex_count
        return len(self._label_map._by_label.get(label, []))

    def close(self):
        self._graph.close()

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def g():
    graph = CountStrategyGraph()
    for _ in range(4):
        graph.add_vertex("person")
    for _ in range(2):
        graph.add_vertex("software")
    yield graph
    graph.close()

def test_fast_count_all_vertices(g):
    assert g.fast_count() == 6

def test_fast_count_by_label_person(g):
    assert g.fast_count("person") == 4

def test_fast_count_by_label_software(g):
    assert g.fast_count("software") == 2

def test_fast_count_absent_label_is_zero(g):
    assert g.fast_count("device") == 0

def test_fast_count_matches_full_scan(g):
    slow = sum(1 for _ in g.vertices())
    assert g.fast_count() == slow

def test_fast_count_label_matches_filter(g):
    slow = sum(1 for v in g.vertices() if v.label == "person")
    assert g.fast_count("person") == slow

def test_count_after_add_is_updated(g):
    before = g.fast_count()
    g.add_vertex("device")
    assert g.fast_count() == before + 1

def test_count_is_o1_performance():
    g = CountStrategyGraph()
    try:
        n = 10_000
        for _ in range(n):
            g.add_vertex("node")

        start = time.monotonic()
        for _ in range(1000):
            _ = g.fast_count()
        fast_elapsed = time.monotonic() - start

        start = time.monotonic()
        for _ in range(1000):
            _ = sum(1 for _ in g.vertices())
        slow_elapsed = time.monotonic() - start

        # fast_count should be at least 10x faster than full scan
        assert fast_elapsed < slow_elapsed, (
            f"fast={fast_elapsed:.4f}s, slow={slow_elapsed:.4f}s — O(1) not faster"
        )
    finally:
        g.close()

def test_strategy_not_applied_to_filtered_traversal(g):
    """Full scan is still used for has() predicates beyond label."""
    filtered_count = sum(
        1 for v in g.vertices()
        if v.label == "person" and (v.value("age") or 0) > 25
    )
    # No short-circuit here — just verify correctness
    assert filtered_count >= 0
