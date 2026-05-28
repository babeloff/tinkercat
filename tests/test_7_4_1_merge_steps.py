"""
Tests for Task 7.4.1: mergeV() and mergeE() Upsert Steps.

Validates onCreate/onMatch semantics and idempotency using mock
implementations of the merge step logic.
See docs/project/changelog/task-7.4.1-merge-steps.adoc.
"""

import pytest
from enum import Enum

from tinkercat import TinkerCat

class Merge(Enum):
    onCreate = "onCreate"
    onMatch  = "onMatch"

def merge_v(graph, search_criteria, on_create=None, on_match=None):
    """Pure-Python implementation of mergeV() semantics."""
    label = search_criteria.get("label", "vertex")
    prop_filters = {k: v for k, v in search_criteria.items() if k != "label"}
    candidate = None
    for v in graph.vertices():
        if v.label != label:
            continue
        if all(v.value(k) == val for k, val in prop_filters.items()):
            candidate = v
            break

    if candidate is not None:
        if on_match:
            for k, val in on_match.items():
                if k != "label":
                    candidate.set_property(k, val)
        return candidate
    else:
        create_props = on_create if on_create else search_criteria
        props = {k: v for k, v in create_props.items() if k != "label"}
        lbl = create_props.get("label", label)
        return graph.add_vertex(lbl, **props)

def merge_e(graph, search_criteria, on_create=None, on_match=None):
    """Pure-Python implementation of mergeE() semantics."""
    label    = search_criteria.get("label")
    out_v    = search_criteria.get("out")
    in_v     = search_criteria.get("in")
    prop_filters = {k: v for k, v in search_criteria.items()
                    if k not in ("label", "out", "in")}
    if label is None:
        raise ValueError("mergeE requires a label in search criteria")

    candidate = None
    for e in graph.edges():
        if e.label != label:
            continue
        if out_v and e.out_vertex.id != out_v.id:
            continue
        if in_v and e.in_vertex.id != in_v.id:
            continue
        if all(e.value(k) == val for k, val in prop_filters.items()):
            candidate = e
            break

    if candidate is not None:
        if on_match:
            for k, val in on_match.items():
                if k not in ("label", "out", "in"):
                    candidate.set_property(k, val)
        return candidate
    else:
        create_props = on_create if on_create else search_criteria
        props = {k: v for k, v in create_props.items()
                 if k not in ("label", "out", "in")}
        lbl = create_props.get("label", label)
        assert out_v is not None and in_v is not None
        return graph.add_edge(lbl, out_v, in_v, **props)

# ---------------------------------------------------------------------------
# mergeV tests
# ---------------------------------------------------------------------------

def test_merge_v_creates_when_missing():
    g = TinkerCat()
    try:
        v = merge_v(g, {"label": "person", "email": "alice@example.com"},
                    on_create={"label": "person", "email": "alice@example.com", "created": True})
        assert g.vertex_count == 1
        assert v.value("email") == "alice@example.com"
        assert v.value("created") is True
    finally:
        g.close()

def test_merge_v_matches_existing():
    g = TinkerCat()
    try:
        existing = g.add_vertex("person", email="alice@example.com", lastSeen="old")
        merge_v(g, {"label": "person", "email": "alice@example.com"},
                on_match={"lastSeen": "new"})
        assert g.vertex_count == 1
        assert existing.value("lastSeen") == "new"
    finally:
        g.close()

def test_merge_v_no_on_create_uses_search_criteria():
    g = TinkerCat()
    try:
        v = merge_v(g, {"label": "person", "name": "Bob"})
        assert v.value("name") == "Bob"
    finally:
        g.close()

def test_merge_v_no_on_match_returns_unchanged():
    g = TinkerCat()
    try:
        g.add_vertex("person", email="x@y.com", score=10)
        v = merge_v(g, {"label": "person", "email": "x@y.com"})
        assert v.value("score") == 10
    finally:
        g.close()

def test_merge_v_idempotent():
    g = TinkerCat()
    try:
        criteria = {"label": "person", "email": "alice@example.com"}
        merge_v(g, criteria)
        merge_v(g, criteria)
        assert g.vertex_count == 1
    finally:
        g.close()

# ---------------------------------------------------------------------------
# mergeE tests
# ---------------------------------------------------------------------------

def test_merge_e_creates_edge():
    g = TinkerCat()
    try:
        a = g.add_vertex("person")
        b = g.add_vertex("person")
        e = merge_e(g, {"label": "knows", "out": a, "in": b})
        assert g.edge_count == 1
        assert e.label == "knows"
    finally:
        g.close()

def test_merge_e_matches_existing_edge():
    g = TinkerCat()
    try:
        a = g.add_vertex("person")
        b = g.add_vertex("person")
        existing = g.add_edge("knows", a, b, since="2020")
        result = merge_e(g, {"label": "knows", "out": a, "in": b},
                         on_match={"since": "2024"})
        assert g.edge_count == 1
        assert result.value("since") == "2024"
    finally:
        g.close()

def test_merge_e_requires_label():
    g = TinkerCat()
    try:
        a = g.add_vertex("n")
        b = g.add_vertex("n")
        with pytest.raises(ValueError, match="label"):
            merge_e(g, {"out": a, "in": b})
    finally:
        g.close()

def test_merge_e_idempotent():
    g = TinkerCat()
    try:
        a = g.add_vertex("n")
        b = g.add_vertex("n")
        merge_e(g, {"label": "link", "out": a, "in": b})
        merge_e(g, {"label": "link", "out": a, "in": b})
        assert g.edge_count == 1
    finally:
        g.close()
