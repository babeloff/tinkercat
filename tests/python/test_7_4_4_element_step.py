"""
Tests for Task 7.4.4: element() Step.

All tests call g.traversal().V().properties(...).element() to navigate
from a property back to its owning vertex or edge.  The properties()
traversal step and the element() step are not yet implemented; every
test fails with AttributeError until they are added to GraphTraversal.
See docs/project/changelog/task-7.4.4-element-step.adoc.
"""

import pytest

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    yield graph
    graph.close()


def test_element_step_returns_owning_vertex(g):
    g.add_vertex("person", name="Alice")
    owners = g.traversal().V().properties("name").element().to_list()  # AttributeError
    assert len(owners) == 1
    assert owners[0].label == "person"


def test_element_step_returns_owning_edge(g):
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    g.add_edge("knows", a, b, weight=1.0)
    owners = g.traversal().E().properties("weight").element().to_list()  # AttributeError
    assert len(owners) == 1
    assert owners[0].label == "knows"


def test_element_step_dedup_collapses_multi_property_hits(g):
    g.add_vertex("person", phone1="111", phone2="222")
    owners = (
        g.traversal().V()
        .properties("phone1", "phone2")
        .element()  # AttributeError
        .dedup()
        .to_list()
    )
    assert len(owners) == 1


def test_element_step_empty_input(g):
    result = g.traversal().V().properties("nonexistent").element().to_list()  # AttributeError
    assert result == []


def test_vertex_property_element_round_trip(g):
    g.add_vertex("person", name="Bob")
    owners = g.traversal().V().properties("name").element().to_list()  # AttributeError
    assert owners[0].value("name") == "Bob"


def test_element_step_mixed_types(g):
    g.add_vertex("node", x=1)
    a = g.add_vertex("n")
    b = g.add_vertex("n")
    g.add_edge("link", a, b, y=2)
    vertex_owners = g.traversal().V().has_label("node").properties("x").element().to_list()  # AttributeError
    edge_owners = g.traversal().E().properties("y").element().to_list()  # AttributeError
    assert vertex_owners[0].label == "node"
    assert edge_owners[0].label == "link"


def test_element_has_correct_label(g):
    g.add_vertex("software", name="lop")
    owners = g.traversal().V().properties("name").element().to_list()  # AttributeError
    assert owners[0].label == "software"
