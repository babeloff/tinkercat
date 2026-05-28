"""
Tests for Task 7.7.2: P Predicate Additions.

All tests import P from tinkercat.  That class does not yet exist; every
test fails with ImportError until P predicates are implemented.
See docs/project/changelog/task-7.7.2-p-predicates.adoc.
"""

import pytest
import json

from tinkercat import TinkerCat


def test_starting_with_match():
    from tinkercat import P  # ImportError until implemented
    assert P.starting_with("Al").test("Alice")


def test_starting_with_no_match():
    from tinkercat import P  # ImportError until implemented
    assert not P.starting_with("Al").test("Bob")


def test_starting_with_null_safe():
    from tinkercat import P  # ImportError until implemented
    assert not P.starting_with("Al").test(None)


def test_not_starting_with():
    from tinkercat import P  # ImportError until implemented
    p = P.not_starting_with("Al")
    assert p.test("Bob")
    assert not p.test("Alice")


def test_ending_with_match():
    from tinkercat import P  # ImportError until implemented
    assert P.ending_with("son").test("Jackson")


def test_ending_with_no_match():
    from tinkercat import P  # ImportError until implemented
    assert not P.ending_with("son").test("Alice")


def test_ending_with_null_safe():
    from tinkercat import P  # ImportError until implemented
    assert not P.ending_with("son").test(None)


def test_not_ending_with():
    from tinkercat import P  # ImportError until implemented
    p = P.not_ending_with("son")
    assert p.test("Alice")
    assert not p.test("Jackson")


def test_containing_match():
    from tinkercat import P  # ImportError until implemented
    assert P.containing("li").test("Alice")


def test_containing_no_match():
    from tinkercat import P  # ImportError until implemented
    assert not P.containing("li").test("Bob")


def test_containing_null_safe():
    from tinkercat import P  # ImportError until implemented
    assert not P.containing("li").test(None)


def test_not_containing():
    from tinkercat import P  # ImportError until implemented
    p = P.not_containing("li")
    assert p.test("Bob")
    assert not p.test("Alice")


def test_regexp_simple_match():
    from tinkercat import P  # ImportError until implemented
    assert P.regexp(r"[A-Z][a-z]+").test("Alice")


def test_regexp_no_match():
    from tinkercat import P  # ImportError until implemented
    assert not P.regexp(r"^\d+$").test("abc")


def test_regexp_partial_match():
    from tinkercat import P  # ImportError until implemented
    assert P.regexp(r"\d+").test("abc123def")


def test_regexp_null_safe():
    from tinkercat import P  # ImportError until implemented
    assert not P.regexp(r"\w+").test(None)


def test_negate_starting_with():
    from tinkercat import P  # ImportError until implemented
    p = P.starting_with("Al").negate()
    assert p.test("Bob")
    assert not p.test("Alice")


def test_predicate_in_traversal_filter():
    from tinkercat import P  # ImportError until implemented
    g = TinkerCat()
    try:
        for name in ["Alice", "Bob", "Alan", "Carol"]:
            g.add_vertex("person", name=name)
        result = g.traversal().V().has("name", P.starting_with("A")).to_list()
        names = {v.value("name") for v in result}
        assert names == {"Alice", "Alan"}
    finally:
        g.close()


def test_ending_with_in_traversal_filter():
    from tinkercat import P  # ImportError until implemented
    g = TinkerCat()
    try:
        for email in ["alice@example.com", "bob@test.org", "carol@example.com"]:
            g.add_vertex("user", email=email)
        result = g.traversal().V().has("email", P.ending_with("@example.com")).to_list()
        assert len(result) == 2
    finally:
        g.close()


def test_graphson_serialisation_starting_with():
    from tinkercat import P  # ImportError until implemented
    p = P.starting_with("Al")
    doc = {"@type": "g:P", "@value": {"predicate": "startingWith", "value": p.pattern}}
    text = json.dumps(doc)
    recovered = json.loads(text)
    assert recovered["@value"]["predicate"] == "startingWith"
    assert recovered["@value"]["value"] == "Al"


def test_graphson_serialisation_regexp():
    from tinkercat import P  # ImportError until implemented
    p = P.regexp(r"\d+")
    doc = {"@type": "g:P", "@value": {"predicate": "regexp", "value": p.pattern}}
    text = json.dumps(doc)
    recovered = json.loads(text)
    assert recovered["@value"]["predicate"] == "regexp"
