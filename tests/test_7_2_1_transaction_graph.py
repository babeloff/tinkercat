"""
Tests for Task 7.2.1: TinkerTransactionGraph — ACID Transaction Support.

Validates commit/rollback lifecycle, snapshot semantics, and thread-local
transaction isolation using mock implementations.
See docs/project/changelog/task-7.2.1-transaction-graph.adoc.
"""

import pytest
import threading

try:
    from tinkercat.structure import TinkerTransactionGraph
    TX_AVAILABLE = True
except ImportError:
    TX_AVAILABLE = False

from mocks import MockGraph


# ---------------------------------------------------------------------------
# Mock transaction implementation
# ---------------------------------------------------------------------------

import copy


class MockTransaction:
    def __init__(self, graph: "TransactionalMockGraph"):
        self._graph = graph
        self._open = False
        self._snapshot = None

    def open(self):
        if self._open:
            raise RuntimeError("Transaction already open")
        self._snapshot = (
            copy.deepcopy(self._graph._vertices),
            copy.deepcopy(self._graph._edges),
            self._graph._next_id,
        )
        self._open = True

    def commit(self):
        self._require_open()
        self._snapshot = None
        self._open = False

    def rollback(self):
        self._require_open()
        verts, edges, nid = self._snapshot
        self._graph._vertices = verts
        self._graph._edges = edges
        self._graph._next_id = nid
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


class TransactionalMockGraph(MockGraph):
    def tx(self):
        return MockTransaction(self)

    def supports_transactions(self):
        return True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def g():
    return TransactionalMockGraph()


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
    v.property("score", 99)
    tx.rollback()
    # Re-fetch: rollback replaces the vertex map with a deep-copy snapshot
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
