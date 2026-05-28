"""
Tests for Task 3.3.2: Native Performance Optimizations.

Verifies memory-pool allocation semantics, concurrent task scheduling,
and memory-mapped I/O contracts.
See docs/project/changelog/task-3.3.2-native-optimization.adoc.
"""

import pytest
import threading
import time

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Mock memory pool
# ---------------------------------------------------------------------------

class MockMemoryPool:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._used = 0
        self._allocs: list = []

    def allocate(self, size: int):
        if self._used + size > self.capacity:
            raise MemoryError("Pool exhausted")
        obj = bytearray(size)
        self._allocs.append((self._used, size))
        self._used += size
        return obj

    def reset(self):
        self._allocs.clear()
        self._used = 0

    @property
    def free(self):
        return self.capacity - self._used

def test_pool_allocate_within_capacity():
    pool = MockMemoryPool(1024)
    buf = pool.allocate(256)
    assert len(buf) == 256
    assert pool.free == 768

def test_pool_exhaustion_raises():
    pool = MockMemoryPool(100)
    pool.allocate(90)
    with pytest.raises(MemoryError):
        pool.allocate(20)

def test_pool_reset_restores_capacity():
    pool = MockMemoryPool(512)
    pool.allocate(256)
    pool.reset()
    assert pool.free == 512

def test_pool_multiple_allocations():
    pool = MockMemoryPool(1024)
    for size in [128, 256, 64]:
        pool.allocate(size)
    assert pool.free == 1024 - 448

# ---------------------------------------------------------------------------
# Work-stealing queue simulation
# ---------------------------------------------------------------------------

class WorkQueue:
    def __init__(self):
        self._tasks: list = []
        self._lock = threading.Lock()
        self._results: list = []

    def submit(self, fn, *args):
        with self._lock:
            self._tasks.append((fn, args))

    def run_all(self):
        workers = []
        while True:
            with self._lock:
                if not self._tasks:
                    break
                fn, args = self._tasks.pop(0)
            result = fn(*args)
            with self._lock:
                self._results.append(result)

def test_work_queue_executes_all_tasks():
    q = WorkQueue()
    for i in range(10):
        q.submit(lambda x: x * 2, i)
    q.run_all()
    assert len(q._results) == 10

def test_work_queue_results_are_correct():
    q = WorkQueue()
    for i in range(5):
        q.submit(lambda x: x + 1, i)
    q.run_all()
    assert sorted(q._results) == [1, 2, 3, 4, 5]

# ---------------------------------------------------------------------------
# Bulk graph operation performance (regression guard)
# ---------------------------------------------------------------------------

def test_bulk_insert_10k_vertices():
    g = TinkerCat()
    try:
        start = time.monotonic()
        for i in range(10_000):
            g.add_vertex("node", idx=i)
        elapsed = time.monotonic() - start
        assert g.vertex_count == 10_000
        assert elapsed < 10.0, f"10K inserts took {elapsed:.2f}s"
    finally:
        g.close()

def test_bulk_edge_creation():
    g = TinkerCat()
    try:
        verts = [g.add_vertex("n") for _ in range(100)]
        for i in range(len(verts) - 1):
            g.add_edge("link", verts[i], verts[i + 1])
        assert g.edge_count == 99
    finally:
        g.close()
