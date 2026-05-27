"""
Tests for Task 4.0.2: Property-Based Testing with Kotest.

Python mirrors of the Kotest property-based tests, using pytest
parametrize and hypothesis-style invariant checks.
See docs/project/changelog/task-4.0.2-kotest-property.adoc.
"""

import pytest
import random

from mocks import MockGraph, build_modern_graph


def random_graph(n_vertices=10, n_edges=15, seed=42):
    rng = random.Random(seed)
    g = MockGraph()
    verts = [g.add_vertex("node", idx=i) for i in range(n_vertices)]
    for _ in range(n_edges):
        a = rng.choice(verts)
        b = rng.choice(verts)
        g.add_edge("e", a, b, weight=rng.random())
    return g


# ── Vertex invariants ──────────────────────────────────────────────────────

@pytest.mark.parametrize("n", [1, 10, 50, 100])
def test_vertex_count_matches_adds(n):
    g = MockGraph()
    for _ in range(n):
        g.add_vertex("node")
    assert g.vertex_count == n


@pytest.mark.parametrize("seed", [0, 1, 42, 99])
def test_vertex_ids_are_unique(seed):
    g = random_graph(seed=seed)
    ids = [v.id for v in g.vertices()]
    assert len(ids) == len(set(ids))


def test_vertex_property_round_trip():
    for val in [0, 1, -1, 2**31 - 1, "hello", "unicode: こんにちは", 3.14, True, False]:
        g = MockGraph()
        v = g.add_vertex("item", data=val)
        assert v.value("data") == val


# ── Edge invariants ────────────────────────────────────────────────────────

@pytest.mark.parametrize("n_verts,n_edges", [(5, 4), (10, 20), (3, 1)])
def test_edge_count_matches_adds(n_verts, n_edges):
    g = random_graph(n_vertices=n_verts, n_edges=n_edges)
    assert g.edge_count == n_edges


@pytest.mark.parametrize("seed", [0, 7, 42])
def test_edge_endpoints_exist_as_vertices(seed):
    g = random_graph(seed=seed)
    vertex_ids = {v.id for v in g.vertices()}
    for e in g.edges():
        assert e.out_vertex.id in vertex_ids
        assert e.in_vertex.id in vertex_ids


# ── Algorithm invariants ───────────────────────────────────────────────────

@pytest.mark.parametrize("seed", [1, 2, 3, 4])
def test_bfs_visits_at_most_all_vertices(seed):
    g = random_graph(n_vertices=20, n_edges=30, seed=seed)
    start = next(iter(g.vertices()))
    visited = set()
    queue = [start]
    while queue:
        v = queue.pop(0)
        if v.id in visited:
            continue
        visited.add(v.id)
        queue.extend(v.out_vertices())
    assert len(visited) <= g.vertex_count


def test_shortest_path_length_non_negative():
    g = random_graph(n_vertices=10, n_edges=15, seed=5)
    src = next(iter(g.vertices()))
    from collections import deque
    dist = {src.id: 0}
    q = deque([src])
    while q:
        v = q.popleft()
        for n in v.out_vertices():
            if n.id not in dist:
                dist[n.id] = dist[v.id] + 1
                q.append(n)
    for d in dist.values():
        assert d >= 0


def test_connected_component_size_bounded():
    g = random_graph(n_vertices=15, n_edges=20, seed=6)
    all_ids = {v.id for v in g.vertices()}
    start = next(iter(g.vertices()))
    reachable = set()
    stack = [start]
    while stack:
        v = stack.pop()
        if v.id in reachable:
            continue
        reachable.add(v.id)
        stack.extend(v.out_vertices())
    assert 1 <= len(reachable) <= len(all_ids)
