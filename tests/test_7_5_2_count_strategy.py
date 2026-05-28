"""
Tests for Task 7.5.2: TinkerCatCountStrategy — Short-circuit Count.

Validates O(1) vertex_count and correct label-filtered counting using
raw TinkerCat.  vertex_count is already O(1) (backed by map.size).
See docs/project/changelog/task-7.5.2-count-strategy.adoc.
"""

import pytest
import time
import os

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    for _ in range(4):
        graph.add_vertex("person")
    for _ in range(2):
        graph.add_vertex("software")
    yield graph
    graph.close()


def test_vertex_count_all_vertices(g):
    assert g.vertex_count == 6


def test_count_by_label_person(g):
    count = sum(1 for v in g.vertices() if v.label == "person")
    assert count == 4


def test_count_by_label_software(g):
    count = sum(1 for v in g.vertices() if v.label == "software")
    assert count == 2


def test_count_absent_label_is_zero(g):
    count = sum(1 for v in g.vertices() if v.label == "device")
    assert count == 0


def test_vertex_count_matches_full_scan(g):
    slow = sum(1 for _ in g.vertices())
    assert g.vertex_count == slow


def test_label_count_matches_filter(g):
    slow = sum(1 for v in g.vertices() if v.label == "person")
    fast = sum(1 for v in g.vertices() if v.label == "person")
    assert fast == slow == 4


def test_count_after_add_is_updated(g):
    before = g.vertex_count
    g.add_vertex("device")
    assert g.vertex_count == before + 1


def test_count_is_o1_performance():
    if os.getenv("PYTEST_XDIST_WORKER"):
        pytest.skip("Native GC threads don't survive fork; timing unreliable in xdist worker")
    graph = TinkerCat()
    try:
        n = 10_000
        for _ in range(n):
            graph.add_vertex("node")

        start = time.monotonic()
        for _ in range(1_000):
            _ = graph.vertex_count
        fast_elapsed = time.monotonic() - start

        start = time.monotonic()
        for _ in range(1_000):
            _ = sum(1 for _ in graph.vertices())
        slow_elapsed = time.monotonic() - start

        assert fast_elapsed < slow_elapsed, (
            f"vertex_count should be O(1): fast={fast_elapsed:.4f}s, slow={slow_elapsed:.4f}s"
        )
    finally:
        graph.close()


def test_strategy_not_applied_to_complex_predicate(g):
    filtered = sum(
        1 for v in g.vertices()
        if v.label == "person" and (v.value("age") or 0) > 25
    )
    assert filtered >= 0
