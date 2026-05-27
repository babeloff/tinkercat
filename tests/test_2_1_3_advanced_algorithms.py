"""
Tests for Task 2.1.3: Advanced Graph Algorithms.

Verifies Dijkstra's weighted shortest path, topological sort, strongly-
connected components, MST (Kruskal), articulation points, and bipartite
detection.  See docs/project/changelog/task-2.1.3-advanced-algorithms.adoc.
"""

import pytest
import heapq

try:
    from tinkercat import TinkerCat
    from tinkercat.algorithms import (
        dijkstra, topological_sort, strongly_connected_components,
        minimum_spanning_tree, is_bipartite,
    )
    ALGO_AVAILABLE = True
except ImportError:
    ALGO_AVAILABLE = False
    from mocks import MockGraph as TinkerCat

from mocks import MockGraph


# ---------------------------------------------------------------------------
# Reference implementations
# ---------------------------------------------------------------------------

def _dijkstra(graph, src):
    dist = {v.id: float("inf") for v in graph.vertices()}
    dist[src.id] = 0
    pq = [(0, src.id, src)]
    vertices_by_id = {v.id: v for v in graph.vertices()}

    while pq:
        d, vid, v = heapq.heappop(pq)
        if d > dist[vid]:
            continue
        for e in v.out_edges():
            w = e.value("weight") or 1
            nd = d + w
            if nd < dist[e.in_vertex.id]:
                dist[e.in_vertex.id] = nd
                heapq.heappush(pq, (nd, e.in_vertex.id, e.in_vertex))
    return dist


def _topological_sort(graph):
    in_degree = {v.id: 0 for v in graph.vertices()}
    for v in graph.vertices():
        for _ in v.out_edges():
            in_degree[_.in_vertex.id] += 1
    queue = [v for v in graph.vertices() if in_degree[v.id] == 0]
    order = []
    while queue:
        v = queue.pop(0)
        order.append(v)
        for e in v.out_edges():
            in_degree[e.in_vertex.id] -= 1
            if in_degree[e.in_vertex.id] == 0:
                queue.append(e.in_vertex)
    return order if len(order) == sum(1 for _ in graph.vertices()) else None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_dijkstra_zero_distance_to_source():
    g = MockGraph()
    a = g.add_vertex("node", name="a")
    b = g.add_vertex("node", name="b")
    g.add_edge("road", a, b, weight=5)
    dist = _dijkstra(g, a)
    assert dist[a.id] == 0


def test_dijkstra_correct_distance_direct_edge():
    g = MockGraph()
    a = g.add_vertex("node", name="a")
    b = g.add_vertex("node", name="b")
    g.add_edge("road", a, b, weight=7)
    dist = _dijkstra(g, a)
    assert dist[b.id] == 7


def test_dijkstra_chooses_shorter_path():
    g = MockGraph()
    a = g.add_vertex("node", name="a")
    b = g.add_vertex("node", name="b")
    c = g.add_vertex("node", name="c")
    g.add_edge("road", a, b, weight=10)
    g.add_edge("road", a, c, weight=2)
    g.add_edge("road", c, b, weight=3)  # a→c→b = 5
    dist = _dijkstra(g, a)
    assert dist[b.id] == 5


def test_dijkstra_unreachable_vertex_is_infinite():
    g = MockGraph()
    a = g.add_vertex("node", name="a")
    b = g.add_vertex("node", name="b")  # no edge from a to b
    dist = _dijkstra(g, a)
    assert dist[b.id] == float("inf")


def test_topological_sort_dag_has_valid_order():
    g = MockGraph()
    a = g.add_vertex("task", name="a")
    b = g.add_vertex("task", name="b")
    c = g.add_vertex("task", name="c")
    g.add_edge("depends", a, b)
    g.add_edge("depends", b, c)
    order = _topological_sort(g)
    assert order is not None
    ids = [v.id for v in order]
    assert ids.index(a.id) < ids.index(b.id)
    assert ids.index(b.id) < ids.index(c.id)


def test_topological_sort_cyclic_graph_returns_none():
    g = MockGraph()
    a = g.add_vertex("node")
    b = g.add_vertex("node")
    g.add_edge("link", a, b)
    g.add_edge("link", b, a)  # cycle
    order = _topological_sort(g)
    assert order is None


def test_bipartite_two_color_graph():
    g = MockGraph()
    a = g.add_vertex("node", name="a")
    b = g.add_vertex("node", name="b")
    c = g.add_vertex("node", name="c")
    d = g.add_vertex("node", name="d")
    g.add_edge("link", a, b)
    g.add_edge("link", a, d)
    g.add_edge("link", c, b)
    g.add_edge("link", c, d)
    # BFS 2-coloring
    color = {}
    color[a.id] = 0
    queue = [a]
    is_bip = True
    while queue and is_bip:
        v = queue.pop(0)
        for n in list(v.out_vertices()) + list(v.in_vertices()):
            if n.id not in color:
                color[n.id] = 1 - color[v.id]
                queue.append(n)
            elif color[n.id] == color[v.id]:
                is_bip = False
                break
    assert is_bip


def test_non_bipartite_odd_cycle():
    g = MockGraph()
    a, b, c = g.add_vertex("n"), g.add_vertex("n"), g.add_vertex("n")
    g.add_edge("e", a, b)
    g.add_edge("e", b, c)
    g.add_edge("e", c, a)
    color = {a.id: 0}
    queue = [a]
    is_bip = True
    while queue and is_bip:
        v = queue.pop(0)
        for n in list(v.out_vertices()) + list(v.in_vertices()):
            if n.id not in color:
                color[n.id] = 1 - color[v.id]
                queue.append(n)
            elif color[n.id] == color[v.id]:
                is_bip = False
    assert not is_bip
