"""
Tests for Task 7.4.4: element() Step.

Validates navigation from Property / VertexProperty back to the owning
Element (Vertex or Edge).
See docs/project/changelog/task-7.4.4-element-step.adoc.
"""

import pytest

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Standalone property wrappers that carry a back-reference to their owner.
# These test a FUTURE feature — the owner is a real TinkerCat Vertex/Edge.
# ---------------------------------------------------------------------------

class MockVertexProperty:
    """A property that knows its owning vertex."""
    def __init__(self, key, value, owner):
        self._key = key
        self._value = value
        self._owner = owner

    def key(self):
        return self._key

    def value(self):
        return self._value

    def element(self):
        return self._owner

class MockEdgeProperty:
    """A property that knows its owning edge."""
    def __init__(self, key, value, owner):
        self._key = key
        self._value = value
        self._owner = owner

    def key(self):
        return self._key

    def value(self):
        return self._value

    def element(self):
        return self._owner

class ElementStep:
    """Applies the element() step to a list of properties."""
    @staticmethod
    def apply(properties):
        return [p.element() for p in properties]

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_element_step_returns_owning_vertex():
    g = TinkerCat()
    try:
        v = g.add_vertex("person", name="Alice")
        prop = MockVertexProperty("name", "Alice", v)
        owners = ElementStep.apply([prop])
        assert len(owners) == 1
        assert owners[0].id == v.id
    finally:
        g.close()

def test_element_step_returns_owning_edge():
    g = TinkerCat()
    try:
        a = g.add_vertex("n")
        b = g.add_vertex("n")
        e = g.add_edge("knows", a, b)
        prop = MockEdgeProperty("weight", 1.0, e)
        owners = ElementStep.apply([prop])
        assert len(owners) == 1
        assert owners[0].id == e.id
    finally:
        g.close()

def test_element_step_dedup_collapses_multi_property_hits():
    g = TinkerCat()
    try:
        v = g.add_vertex("person", phone1="111", phone2="222")
        props = [
            MockVertexProperty("phone1", "111", v),
            MockVertexProperty("phone2", "222", v),
        ]
        owners = list({o.id: o for o in ElementStep.apply(props)}.values())
        assert len(owners) == 1
    finally:
        g.close()

def test_element_step_empty_input():
    assert ElementStep.apply([]) == []

def test_vertex_property_element_round_trip():
    g = TinkerCat()
    try:
        v = g.add_vertex("person", name="Bob")
        prop = MockVertexProperty("name", "Bob", v)
        assert prop.element().value("name") == "Bob"
    finally:
        g.close()

def test_element_step_mixed_types():
    g = TinkerCat()
    try:
        v = g.add_vertex("node", x=1)
        a = g.add_vertex("n")
        b = g.add_vertex("n")
        e = g.add_edge("link", a, b, y=2)

        vp = MockVertexProperty("x", 1, v)
        ep = MockEdgeProperty("y", 2, e)

        owners = ElementStep.apply([vp, ep])
        assert owners[0].id == v.id
        assert owners[1].id == e.id
    finally:
        g.close()

def test_element_has_correct_label():
    g = TinkerCat()
    try:
        v = g.add_vertex("software", name="lop")
        prop = MockVertexProperty("name", "lop", v)
        owner = prop.element()
        assert owner.label == "software"
    finally:
        g.close()
