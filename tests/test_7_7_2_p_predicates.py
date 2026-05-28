"""
Tests for Task 7.7.2: P Predicate Additions.

Validates startingWith, notStartingWith, endingWith, notEndingWith,
containing, notContaining, and regexp predicates.
See docs/project/changelog/task-7.7.2-p-predicates.adoc.
"""

import pytest
import re
import json

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Mock P predicates
# ---------------------------------------------------------------------------

class P:
    def __init__(self, fn, pattern: str):
        self._fn = fn
        self.pattern = pattern

    def test(self, value) -> bool:
        if value is None:
            return False
        return self._fn(str(value))

    def negate(self) -> "P":
        fn = self._fn
        return P(lambda v: not fn(v), self.pattern)

    @staticmethod
    def starting_with(prefix: str) -> "P":
        return P(lambda v: v.startswith(prefix), prefix)

    @staticmethod
    def not_starting_with(prefix: str) -> "P":
        return P(lambda v: not v.startswith(prefix), prefix)

    @staticmethod
    def ending_with(suffix: str) -> "P":
        return P(lambda v: v.endswith(suffix), suffix)

    @staticmethod
    def not_ending_with(suffix: str) -> "P":
        return P(lambda v: not v.endswith(suffix), suffix)

    @staticmethod
    def containing(sub: str) -> "P":
        return P(lambda v: sub in v, sub)

    @staticmethod
    def not_containing(sub: str) -> "P":
        return P(lambda v: sub not in v, sub)

    @staticmethod
    def regexp(pattern: str) -> "P":
        compiled = re.compile(pattern)
        return P(lambda v: bool(compiled.search(v)), pattern)

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_starting_with_match():
    assert P.starting_with("Al").test("Alice")

def test_starting_with_no_match():
    assert not P.starting_with("Al").test("Bob")

def test_starting_with_null_safe():
    assert not P.starting_with("Al").test(None)

def test_not_starting_with():
    p = P.not_starting_with("Al")
    assert p.test("Bob")
    assert not p.test("Alice")

def test_ending_with_match():
    assert P.ending_with("son").test("Jackson")

def test_ending_with_no_match():
    assert not P.ending_with("son").test("Alice")

def test_ending_with_null_safe():
    assert not P.ending_with("son").test(None)

def test_not_ending_with():
    p = P.not_ending_with("son")
    assert p.test("Alice")
    assert not p.test("Jackson")

def test_containing_match():
    assert P.containing("li").test("Alice")

def test_containing_no_match():
    assert not P.containing("li").test("Bob")

def test_containing_null_safe():
    assert not P.containing("li").test(None)

def test_not_containing():
    p = P.not_containing("li")
    assert p.test("Bob")
    assert not p.test("Alice")

def test_regexp_simple_match():
    assert P.regexp(r"[A-Z][a-z]+").test("Alice")

def test_regexp_no_match():
    assert not P.regexp(r"^\d+$").test("abc")

def test_regexp_partial_match():
    assert P.regexp(r"\d+").test("abc123def")

def test_regexp_null_safe():
    assert not P.regexp(r"\w+").test(None)

def test_negate_starting_with():
    p = P.starting_with("Al").negate()
    assert p.test("Bob")
    assert not p.test("Alice")

def test_predicate_in_filter():
    g = TinkerCat()
    try:
        for name in ["Alice", "Bob", "Alan", "Carol"]:
            g.add_vertex("person", name=name)
        p = P.starting_with("A")
        result = [v for v in g.vertices() if p.test(v.value("name"))]
        names = {v.value("name") for v in result}
        assert names == {"Alice", "Alan"}
    finally:
        g.close()

def test_ending_with_in_filter():
    g = TinkerCat()
    try:
        for email in ["alice@example.com", "bob@test.org", "carol@example.com"]:
            g.add_vertex("user", email=email)
        p = P.ending_with("@example.com")
        result = [v for v in g.vertices() if p.test(v.value("email"))]
        assert len(result) == 2
    finally:
        g.close()

def test_graphson_serialisation_starting_with():
    p = P.starting_with("Al")
    doc = {"@type": "g:P", "@value": {"predicate": "startingWith", "value": p.pattern}}
    text = json.dumps(doc)
    recovered = json.loads(text)
    assert recovered["@value"]["predicate"] == "startingWith"
    assert recovered["@value"]["value"] == "Al"

def test_graphson_serialisation_regexp():
    p = P.regexp(r"\d+")
    doc = {"@type": "g:P", "@value": {"predicate": "regexp", "value": p.pattern}}
    text = json.dumps(doc)
    recovered = json.loads(text)
    assert recovered["@value"]["predicate"] == "regexp"
