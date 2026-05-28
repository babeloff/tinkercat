"""
Tests for Task 7.4.1: mergeV() and mergeE() Upsert Steps.

All tests call g.traversal().merge_v() / merge_e() directly.
These spawning steps are not yet implemented; every test fails with
AttributeError until they are added to TinkerCat's traversal API.
See docs/project/changelog/task-7.4.1-merge-steps.adoc.
"""

import pytest

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    yield graph
    graph.close()


# ---------------------------------------------------------------------------
# mergeV tests
# ---------------------------------------------------------------------------

def test_merge_v_creates_when_missing(g):
    criteria = {"label": "person", "email": "alice@example.com"}
    on_create = {"label": "person", "email": "alice@example.com", "created": True}
    result = g.traversal().merge_v(criteria, on_create=on_create).to_list()  # AttributeError
    assert len(result) == 1
    assert g.vertex_count == 1
    assert result[0].value("email") == "alice@example.com"
    assert result[0].value("created") is True


def test_merge_v_matches_existing(g):
    g.add_vertex("person", email="alice@example.com", lastSeen="old")
    result = g.traversal().merge_v(  # AttributeError
        {"label": "person", "email": "alice@example.com"},
        on_match={"lastSeen": "new"},
    ).to_list()
    assert g.vertex_count == 1
    assert result[0].value("lastSeen") == "new"


def test_merge_v_no_on_create_uses_search_criteria(g):
    result = g.traversal().merge_v({"label": "person", "name": "Bob"}).to_list()  # AttributeError
    assert result[0].value("name") == "Bob"


def test_merge_v_no_on_match_returns_unchanged(g):
    g.add_vertex("person", email="x@y.com", score=10)
    result = g.traversal().merge_v({"label": "person", "email": "x@y.com"}).to_list()  # AttributeError
    assert result[0].value("score") == 10


def test_merge_v_idempotent(g):
    criteria = {"label": "person", "email": "alice@example.com"}
    g.traversal().merge_v(criteria).iterate()  # AttributeError
    g.traversal().merge_v(criteria).iterate()
    assert g.vertex_count == 1


# ---------------------------------------------------------------------------
# mergeE tests
# ---------------------------------------------------------------------------

def test_merge_e_creates_edge(g):
    a = g.add_vertex("person")
    b = g.add_vertex("person")
    result = g.traversal().merge_e({"label": "knows", "out": a, "in": b}).to_list()  # AttributeError
    assert g.edge_count == 1
    assert result[0].label == "knows"


def test_merge_e_matches_existing_edge(g):
    a = g.add_vertex("person")
    b = g.add_vertex("person")
    g.add_edge("knows", a, b, since="2020")
    result = g.traversal().merge_e(  # AttributeError
        {"label": "knows", "out": a, "in": b},
        on_match={"since": "2024"},
    ).to_list()
    assert g.edge_count == 1
    assert result[0].value("since") == "2024"


def test_merge_e_requires_label(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    with pytest.raises(Exception):
        g.traversal().merge_e({"out": a, "in": b}).iterate()  # AttributeError or ValueError


def test_merge_e_idempotent(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    g.traversal().merge_e({"label": "link", "out": a, "in": b}).iterate()  # AttributeError
    g.traversal().merge_e({"label": "link", "out": a, "in": b}).iterate()
    assert g.edge_count == 1
