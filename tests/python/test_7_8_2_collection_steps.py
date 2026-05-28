"""
Tests for Task 7.8.2: Collection / Set Traversal Steps.

Covers all() and any() (implemented) and the unimplemented stubs:
difference, disjunct, intersect, conjoin, combine, product, merge.
Mirrors tests/kotlin/test_7_8_2_collection_steps.kt.
"""

import pytest

from tinkercat import TinkerCat, P


# ── all ───────────────────────────────────────────────────────────────────────

def test_all_keeps_scalar_passing_predicate():
    g = TinkerCat()
    try:
        g.add_vertex("e", score=10)
        result = g.traversal().V().values("score").all(P.gt(5)).to_list()
        assert len(result) == 1
    finally:
        g.close()


def test_all_removes_scalar_failing_predicate():
    g = TinkerCat()
    try:
        g.add_vertex("e", score=3)
        result = g.traversal().V().values("score").all(P.gt(5)).to_list()
        assert len(result) == 0
    finally:
        g.close()


def test_all_keeps_list_when_all_pass():
    g = TinkerCat()
    try:
        g.add_vertex("e", nums=[5, 6, 7])
        result = g.traversal().V().values("nums").all(P.gt(3)).to_list()
        assert len(result) == 1
    finally:
        g.close()


def test_all_removes_list_when_any_fail():
    g = TinkerCat()
    try:
        g.add_vertex("e", nums=[5, 6, 2])
        result = g.traversal().V().values("nums").all(P.gt(3)).to_list()
        assert len(result) == 0
    finally:
        g.close()


def test_all_on_mixed_vertices():
    g = TinkerCat()
    try:
        g.add_vertex("e", nums=[10, 20, 30])
        g.add_vertex("e", nums=[10, 20, 2])
        result = g.traversal().V().values("nums").all(P.gt(5)).to_list()
        assert len(result) == 1
    finally:
        g.close()


# ── any ───────────────────────────────────────────────────────────────────────

def test_any_keeps_scalar_passing_predicate():
    g = TinkerCat()
    try:
        g.add_vertex("e", score=10)
        result = g.traversal().V().values("score").any(P.gt(5)).to_list()
        assert len(result) == 1
    finally:
        g.close()


def test_any_removes_scalar_failing_predicate():
    g = TinkerCat()
    try:
        g.add_vertex("e", score=3)
        result = g.traversal().V().values("score").any(P.gt(5)).to_list()
        assert len(result) == 0
    finally:
        g.close()


def test_any_keeps_list_when_one_passes():
    g = TinkerCat()
    try:
        g.add_vertex("e", nums=[1, 2, 10])
        result = g.traversal().V().values("nums").any(P.gt(5)).to_list()
        assert len(result) == 1
    finally:
        g.close()


def test_any_removes_list_when_none_pass():
    g = TinkerCat()
    try:
        g.add_vertex("e", nums=[1, 2, 3])
        result = g.traversal().V().values("nums").any(P.gt(5)).to_list()
        assert len(result) == 0
    finally:
        g.close()


def test_any_on_mixed_vertices():
    g = TinkerCat()
    try:
        g.add_vertex("e", nums=[1, 2, 10])
        g.add_vertex("e", nums=[1, 2,  3])
        result = g.traversal().V().values("nums").any(P.gt(5)).to_list()
        assert len(result) == 1
    finally:
        g.close()


# ── unimplemented stubs ───────────────────────────────────────────────────────

def test_difference_raises_not_implemented():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=1)
        with pytest.raises(NotImplementedError):
            g.traversal().V().values("v").difference({1}).to_list()
    finally:
        g.close()


def test_disjunct_raises_not_implemented():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=1)
        with pytest.raises(NotImplementedError):
            g.traversal().V().values("v").disjunct({1}).to_list()
    finally:
        g.close()


def test_intersect_raises_not_implemented():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=1)
        with pytest.raises(NotImplementedError):
            g.traversal().V().values("v").intersect({1}).to_list()
    finally:
        g.close()


def test_conjoin_raises_not_implemented():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=1)
        with pytest.raises(NotImplementedError):
            g.traversal().V().values("v").conjoin(",").to_list()
    finally:
        g.close()


def test_combine_raises_not_implemented():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=1)
        with pytest.raises(NotImplementedError):
            g.traversal().V().values("v").combine([1]).to_list()
    finally:
        g.close()


def test_product_raises_not_implemented():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=1)
        with pytest.raises(NotImplementedError):
            g.traversal().V().values("v").product([1]).to_list()
    finally:
        g.close()


def test_merge_raises_not_implemented():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=1)
        with pytest.raises(NotImplementedError):
            g.traversal().V().values("v").merge({"a": 1}).to_list()
    finally:
        g.close()
