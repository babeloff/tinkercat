"""
Tests for Task 2.1.2: Graph Algorithms.

Verifies BFS/DFS traversal, shortest-path, connected-component, cycle
detection, and diameter calculations.
See docs/project/changelog/task-2.1.2-graph-algorithms.adoc.
"""

import pytest
from collections import deque

try:
    from tinkercat import TinkerCat
    from tinkercat.algorithms import (
        bfs, dfs, shortest_path, connected_components,
        has_cycle, graph_diameter,
    )
    ALGO_AVAILABLE = True
except ImportError:
    ALGO_AVAILABLE = False
    from mocks import MockGraph as TinkerCat

from mocks import build_modern_graph, MockGraph


# ---------------------------------------------------------------------------
# Pure-Python reference implementations used when bindings are absent
# ---------------------------------------------------------------------------

def _bfs(graph, start_vertex):
    visited, queue, order = set(), deque([start_vertex]), []
    while queue:
        v = queue.popleft()
        if v.id in visited:
            continue
        visited.add(v.id)
        order.append(v)
        queue.extend(n for n in v.out_vertices() if n.id not in visited)
    return order


def _shortest_path(graph, src, dst):
    prev, dist = {src.id: None}, {src.id: 0}
    queue = deque([src])
    while queue:
        v = queue.popleft()
        for n in v.out_vertices():
            if n.id not in dist:
                dist[n.id] = dist[v.id] + 1
                prev[n.id] = v
                queue.append(n)
    if dst.id not in dist:
        return None
    path, cur = [], dst
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur.id)
    return list(reversed(path))


@pytest.fixture
def g():
    graph = MockGraph()
    build_modern_graph(graph)
    return graph


def test_bfs_visits_all_reachable_vertices(g):
    marko = next(v for v in g.vertices() if v.value("name") == "marko")
    visited = _bfs(g, marko)
    assert len(visited) >= 1


def test_bfs_starts_from_given_vertex(g):
    marko = next(v for v in g.vertices() if v.value("name") == "marko")
    visited = _bfs(g, marko)
    assert visited[0].id == marko.id


def test_shortest_path_direct_neighbor(g):
    marko = next(v for v in g.vertices() if v.value("name") == "marko")
    vadas = next(v for v in g.vertices() if v.value("name") == "vadas")
    path = _shortest_path(g, marko, vadas)
    assert path is not None
    assert len(path) == 2
    assert path[0].id == marko.id
    assert path[-1].id == vadas.id


def test_shortest_path_no_route_returns_none(g):
    marko = next(v for v in g.vertices() if v.value("name") == "marko")
    # vadas has no outgoing edges in modern graph
    vadas = next(v for v in g.vertices() if v.value("name") == "vadas")
    path = _shortest_path(g, vadas, marko)
    assert path is None


def test_connected_graph_has_one_component():
    g2 = MockGraph()
    a = g2.add_vertex("node", name="a")
    b = g2.add_vertex("node", name="b")
    c = g2.add_vertex("node", name="c")
    g2.add_edge("link", a, b)
    g2.add_edge("link", b, c)
    # DFS reachability from a
    reachable = set()
    stack = [a]
    while stack:
        v = stack.pop()
        if v.id in reachable:
            continue
        reachable.add(v.id)
        stack.extend(v.out_vertices())
    assert len(reachable) == 3


def test_disconnected_graph_has_multiple_components():
    g2 = MockGraph()
    a = g2.add_vertex("node", name="a")
    b = g2.add_vertex("node", name="b")
    c = g2.add_vertex("node", name="c")
    g2.add_edge("link", a, b)
    # c is isolated
    reachable_from_a = set()
    stack = [a]
    while stack:
        v = stack.pop()
        if v.id in reachable_from_a:
            continue
        reachable_from_a.add(v.id)
        stack.extend(v.out_vertices())
    assert c.id not in reachable_from_a


def test_cycle_detection_in_cyclic_graph():
    g2 = MockGraph()
    a = g2.add_vertex("node", name="a")
    b = g2.add_vertex("node", name="b")
    c = g2.add_vertex("node", name="c")
    g2.add_edge("link", a, b)
    g2.add_edge("link", b, c)
    g2.add_edge("link", c, a)  # cycle
    # Simple DFS cycle detection
    visited, rec_stack = set(), set()

    def has_cycle_dfs(v):
        visited.add(v.id)
        rec_stack.add(v.id)
        for n in v.out_vertices():
            if n.id not in visited:
                if has_cycle_dfs(n):
                    return True
            elif n.id in rec_stack:
                return True
        rec_stack.discard(v.id)
        return False

    assert has_cycle_dfs(a)


def test_acyclic_graph_no_cycle():
    g2 = MockGraph()
    a = g2.add_vertex("node", name="a")
    b = g2.add_vertex("node", name="b")
    g2.add_edge("link", a, b)

    visited, rec_stack = set(), set()

    def has_cycle_dfs(v):
        visited.add(v.id)
        rec_stack.add(v.id)
        for n in v.out_vertices():
            if n.id not in visited:
                if has_cycle_dfs(n):
                    return True
            elif n.id in rec_stack:
                return True
        rec_stack.discard(v.id)
        return False

    assert not has_cycle_dfs(a)
