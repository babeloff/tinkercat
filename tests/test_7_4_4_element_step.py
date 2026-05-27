"""
Tests for Task 7.4.4: element() Step.

Validates navigation from Property / VertexProperty back to the owning
Element (Vertex or Edge).
See docs/project/changelog/task-7.4.4-element-step.adoc.
"""

import pytest

from mocks import MockGraph, MockVertex, MockEdge, MockProperty


# ---------------------------------------------------------------------------
# Mock element-step implementation
# ---------------------------------------------------------------------------

class MockVertexProperty(MockProperty):
    """A property that knows its owning vertex."""
    def __init__(self, key, value, owner: MockVertex):
        super().__init__(key, value)
        self._owner = owner

    def element(self) -> MockVertex:
        return self._owner


class MockEdgeProperty(MockProperty):
    """A property that knows its owning edge."""
    def __init__(self, key, value, owner: MockEdge):
        super().__init__(key, value)
        self._owner = owner

    def element(self) -> MockEdge:
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
    g = MockGraph()
    v = g.add_vertex("person", name="Alice")
    prop = MockVertexProperty("name", "Alice", v)
    owners = ElementStep.apply([prop])
    assert len(owners) == 1
    assert owners[0].id == v.id


def test_element_step_returns_owning_edge():
    g = MockGraph()
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("knows", a, b)
    prop = MockEdgeProperty("weight", 1.0, e)
    owners = ElementStep.apply([prop])
    assert len(owners) == 1
    assert owners[0].id == e.id


def test_element_step_dedup_collapses_multi_property_hits():
    g = MockGraph()
    v = g.add_vertex("person", phone1="111", phone2="222")
    props = [
        MockVertexProperty("phone1", "111", v),
        MockVertexProperty("phone2", "222", v),
    ]
    owners = list({o.id: o for o in ElementStep.apply(props)}.values())
    assert len(owners) == 1


def test_element_step_empty_input():
    assert ElementStep.apply([]) == []


def test_vertex_property_element_round_trip():
    g = MockGraph()
    v = g.add_vertex("person", name="Bob")
    prop = MockVertexProperty("name", "Bob", v)
    assert prop.element().value("name") == "Bob"


def test_element_step_mixed_types():
    g = MockGraph()
    v = g.add_vertex("node", x=1)
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    e = g.add_edge("link", a, b, y=2)

    vp = MockVertexProperty("x", 1, v)
    ep = MockEdgeProperty("y", 2, e)

    owners = ElementStep.apply([vp, ep])
    assert owners[0].id == v.id
    assert owners[1].id == e.id


def test_element_has_correct_label():
    g = MockGraph()
    v = g.add_vertex("software", name="lop")
    prop = MockVertexProperty("name", "lop", v)
    owner = prop.element()
    assert owner.label == "software"
