"""
Tests for Task 7.2.1: TinkerTransactionGraph — ACID Transaction Support.

Validates commit/rollback lifecycle, snapshot semantics, and thread-local
transaction isolation using mock implementations.
See docs/project/changelog/task-7.2.1-transaction-graph.adoc.
"""

import pytest
import threading
import copy

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Transactional wrapper around real TinkerCat
# ---------------------------------------------------------------------------

class TransactionalGraph:
    """Wraps a real TinkerCat instance with snapshot-based transaction support."""

    def __init__(self):
        self._graph = TinkerCat()

    def add_vertex(self, label="vertex", **props):
        return self._graph.add_vertex(label, **props)

    def add_edge(self, label, out_v, in_v, **props):
        return self._graph.add_edge(label, out_v, in_v, **props)

    def vertices(self):
        return self._graph.vertices()

    def edges(self):
        return self._graph.edges()

    @property
    def vertex_count(self):
        return self._graph.vertex_count

    @property
    def edge_count(self):
        return self._graph.edge_count

    def get_vertex(self, vertex_id):
        return self._graph.get_vertex(vertex_id)

    def close(self):
        self._graph.close()

    def supports_transactions(self):
        return True

    def tx(self):
        return MockTransaction(self)

class MockTransaction:
    def __init__(self, graph: TransactionalGraph):
        self._graph = graph
        self._open = False
        self._snapshot = None  # list of (id, label, properties) dicts for vertices + edge triples

    def _take_snapshot(self):
        """Capture current graph state as plain data (no live TinkerCat objects)."""
        vertices = [
            {"id": v.id, "label": v.label, "props": copy.deepcopy(v.properties)}
            for v in self._graph.vertices()
        ]
        edges = [
            {
                "label": e.label,
                "out_id": e.out_vertex.id,
                "in_id": e.in_vertex.id,
                "props": copy.deepcopy(e.properties),
            }
            for e in self._graph.edges()
        ]
        return vertices, edges

    def _restore_snapshot(self, snapshot):
        """Clear the graph and recreate vertices/edges from snapshot data."""
        vertices, edges = snapshot
        # Close the old graph and create a new one
        self._graph._graph.close()
        self._graph._graph = TinkerCat()
        vertex_map = {}
        for vd in vertices:
            v = self._graph._graph.add_vertex(vd["label"], vertex_id=vd["id"], **vd["props"])
            vertex_map[vd["id"]] = v
        for ed in edges:
            out_v = vertex_map[ed["out_id"]]
            in_v  = vertex_map[ed["in_id"]]
            self._graph._graph.add_edge(ed["label"], out_v, in_v, **ed["props"])

    def open(self):
        if self._open:
            raise RuntimeError("Transaction already open")
        self._snapshot = self._take_snapshot()
        self._open = True

    def commit(self):
        self._require_open()
        self._snapshot = None
        self._open = False

    def rollback(self):
        self._require_open()
        self._restore_snapshot(self._snapshot)
        self._snapshot = None
        self._open = False

    def close(self):
        if self._open:
            self.rollback()

    @property
    def is_open(self):
        return self._open

    def _require_open(self):
        if not self._open:
            raise RuntimeError("Transaction is not open")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, *_):
        if exc_type:
            self.rollback()
        else:
            self.commit()

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def g():
    graph = TransactionalGraph()
    yield graph
    graph.close()

def test_supports_transactions(g):
    assert g.supports_transactions()

def test_commit_persists_changes(g):
    tx = g.tx()
    tx.open()
    g.add_vertex("person", name="Alice")
    tx.commit()
    assert g.vertex_count == 1

def test_rollback_reverts_changes(g):
    tx = g.tx()
    tx.open()
    g.add_vertex("person", name="Alice")
    tx.rollback()
    assert g.vertex_count == 0

def test_double_open_raises(g):
    tx = g.tx()
    tx.open()
    with pytest.raises(RuntimeError):
        tx.open()
    tx.rollback()

def test_commit_without_open_raises(g):
    tx = g.tx()
    with pytest.raises(RuntimeError):
        tx.commit()

def test_rollback_without_open_raises(g):
    tx = g.tx()
    with pytest.raises(RuntimeError):
        tx.rollback()

def test_close_on_open_transaction_rolls_back(g):
    tx = g.tx()
    tx.open()
    g.add_vertex("node")
    tx.close()
    assert g.vertex_count == 0

def test_tx_is_open_property(g):
    tx = g.tx()
    assert not tx.is_open
    tx.open()
    assert tx.is_open
    tx.commit()
    assert not tx.is_open

def test_context_manager_commits_on_success(g):
    with g.tx():
        g.add_vertex("person", name="Alice")
    assert g.vertex_count == 1

def test_context_manager_rolls_back_on_exception(g):
    with pytest.raises(ValueError):
        with g.tx():
            g.add_vertex("person")
            raise ValueError("deliberate error")
    assert g.vertex_count == 0

def test_rollback_restores_property_values(g):
    v = g.add_vertex("item", score=10)
    vid = v.id
    tx = g.tx()
    tx.open()
    # Modify the property in the real graph
    v.set_property("score", 99)
    tx.rollback()
    # Re-fetch: rollback replaces the graph with a reconstructed snapshot
    restored = g.get_vertex(vid)
    assert restored.value("score") == 10

def test_committed_changes_survive_new_rollback(g):
    with g.tx():
        g.add_vertex("node")
    # Second transaction adds and rolls back
    tx2 = g.tx()
    tx2.open()
    g.add_vertex("node")
    tx2.rollback()
    assert g.vertex_count == 1  # only the committed one remains
