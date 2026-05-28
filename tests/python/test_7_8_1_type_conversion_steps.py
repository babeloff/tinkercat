"""
Tests for Task 7.8.1: Type Conversion Traversal Steps.

Covers as_bool() and as_number() steps added in TinkerPop 3.8.0.
Mirrors tests/kotlin/test_7_8_1_type_conversion_steps.kt.
"""

import pytest

from tinkercat import TinkerCat


# ── asBool ────────────────────────────────────────────────────────────────────

def test_as_bool_passthrough_true():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=True)
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [True]
    finally:
        g.close()


def test_as_bool_passthrough_false():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=False)
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [False]
    finally:
        g.close()


def test_as_bool_from_string_true():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="true")
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [True]
    finally:
        g.close()


def test_as_bool_from_string_true_case_insensitive():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="TRUE")
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [True]
    finally:
        g.close()


def test_as_bool_from_string_false():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="false")
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [False]
    finally:
        g.close()


def test_as_bool_from_string_one_is_true():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="1")
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [True]
    finally:
        g.close()


def test_as_bool_from_string_zero_is_false():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="0")
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [False]
    finally:
        g.close()


def test_as_bool_from_nonzero_int_is_true():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=42)
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [True]
    finally:
        g.close()


def test_as_bool_from_zero_int_is_false():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=0)
        result = g.traversal().V().values("v").as_bool().to_list()
        assert result == [False]
    finally:
        g.close()


def test_as_bool_from_unsupported_type_raises():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=[1, 2, 3])
        with pytest.raises((TypeError, ValueError, Exception)):
            g.traversal().V().values("v").as_bool().to_list()
    finally:
        g.close()


# ── asNumber ──────────────────────────────────────────────────────────────────

def test_as_number_passthrough_int():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=42)
        result = g.traversal().V().values("v").as_number().to_list()
        assert result == [42]
    finally:
        g.close()


def test_as_number_passthrough_float():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=3.14)
        result = g.traversal().V().values("v").as_number().to_list()
        assert result == [3.14]
    finally:
        g.close()


def test_as_number_from_string_integer():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="100")
        result = g.traversal().V().values("v").as_number().to_list()
        assert result == [100]
    finally:
        g.close()


def test_as_number_from_string_float():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="2.718")
        result = g.traversal().V().values("v").as_number().to_list()
        assert abs(result[0] - 2.718) < 1e-9
    finally:
        g.close()


def test_as_number_from_bool_true_is_1():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=True)
        result = g.traversal().V().values("v").as_number().to_list()
        assert result == [1]
    finally:
        g.close()


def test_as_number_from_bool_false_is_0():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=False)
        result = g.traversal().V().values("v").as_number().to_list()
        assert result == [0]
    finally:
        g.close()


def test_as_number_from_unparseable_string_raises():
    g = TinkerCat()
    try:
        g.add_vertex("e", v="not-a-number")
        with pytest.raises((ValueError, Exception)):
            g.traversal().V().values("v").as_number().to_list()
    finally:
        g.close()


def test_as_number_from_unsupported_type_raises():
    g = TinkerCat()
    try:
        g.add_vertex("e", v=[1, 2])
        with pytest.raises((TypeError, ValueError, Exception)):
            g.traversal().V().values("v").as_number().to_list()
    finally:
        g.close()


# ── pipeline composition ──────────────────────────────────────────────────────

def test_as_number_then_comparison():
    g = TinkerCat()
    try:
        g.add_vertex("e", score="95")
        result = g.traversal().V().values("score").as_number().to_list()
        assert len(result) == 1
        assert result[0] > 90
    finally:
        g.close()
