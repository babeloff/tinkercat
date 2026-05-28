"""
Tests for Task 7.2.1: TinkerTransactionGraph — ACID Transaction Support.

Validates commit/rollback lifecycle, snapshot semantics, and context-manager
protocol directly against TinkerCat's transaction API.
See docs/project/changelog/task-7.2.1-transaction-graph.adoc.
"""

import pytest

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    yield graph
    graph.close()


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
    with pytest.raises(Exception):
        tx.open()
    tx.rollback()


def test_commit_without_open_raises(g):
    tx = g.tx()
    with pytest.raises(Exception):
        tx.commit()


def test_rollback_without_open_raises(g):
    tx = g.tx()
    with pytest.raises(Exception):
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
    v.set_property("score", 99)
    tx.rollback()
    restored = g.get_vertex(vid)
    assert restored.value("score") == 10


def test_committed_changes_survive_new_rollback(g):
    with g.tx():
        g.add_vertex("node")
    tx2 = g.tx()
    tx2.open()
    g.add_vertex("node")
    tx2.rollback()
    assert g.vertex_count == 1
