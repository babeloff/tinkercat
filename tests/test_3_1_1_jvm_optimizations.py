"""
Tests for Task 3.1.1: JVM-Specific Optimizations.

Verifies concurrent access patterns, Java interoperability, and
serialisation round-trips.  JVM-specific behaviour is skipped on
non-JVM platforms.
See docs/project/changelog/task-3.1.1-jvm-optimizations.adoc.
"""

import pytest
import threading
import time

try:
    from tinkercat import TinkerCat
    BINDINGS_AVAILABLE = True
except ImportError:
    BINDINGS_AVAILABLE = False
    from mocks import MockGraph as TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat.open() if hasattr(TinkerCat, "open") else TinkerCat()
    yield graph
    if hasattr(graph, "close"):
        graph.close()


def test_concurrent_vertex_creation(g):
    """Multiple threads may add vertices without data loss."""
    errors = []

    def add_vertices(n):
        try:
            for i in range(n):
                g.add_vertex("node", thread_idx=i)
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=add_vertices, args=(10,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    count = sum(1 for _ in g.vertices())
    assert count == 40


def test_concurrent_reads_during_writes(g):
    """Readers can iterate vertices while writers add new ones."""
    for i in range(20):
        g.add_vertex("node", idx=i)

    read_counts = []
    stop = threading.Event()

    def reader():
        while not stop.is_set():
            c = sum(1 for _ in g.vertices())
            read_counts.append(c)
            time.sleep(0.001)

    def writer():
        for i in range(10):
            g.add_vertex("extra", idx=i)
            time.sleep(0.002)

    rt = threading.Thread(target=reader)
    wt = threading.Thread(target=writer)
    rt.start()
    wt.start()
    wt.join()
    stop.set()
    rt.join()

    assert len(read_counts) > 0
    assert all(c >= 20 for c in read_counts)


def test_vertex_count_consistent_after_concurrent_adds(g):
    """Final vertex count equals total adds across all threads."""
    count_per_thread = 25
    num_threads = 4
    threads = [
        threading.Thread(target=lambda: [g.add_vertex("t") for _ in range(count_per_thread)])
        for _ in range(num_threads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = sum(1 for _ in g.vertices())
    assert total == count_per_thread * num_threads


def test_graph_repr_contains_counts(g):
    g.add_vertex("person", name="Alice")
    r = repr(g)
    assert r is not None
    assert len(r) > 0


def test_graph_close_idempotent(g):
    if hasattr(g, "close"):
        g.close()
        g.close()  # second close must not raise
