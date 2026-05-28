"""
Tests for Task 7.4.5: call() Service Invocation Step.

All tests call g.traversal().V().call(service_name, context) on a live
TinkerCat graph.  The call() step is not yet implemented; every test
fails with AttributeError until it is added to GraphTraversal.
See docs/project/changelog/task-7.4.5-call-step.adoc.
"""

import pytest

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    yield graph
    graph.close()


def test_call_step_returns_context(g):
    g.add_vertex("person", name="Alice")
    result = g.traversal().V().call("echo", {"hello": "world"}).to_list()  # AttributeError
    assert result == [{"hello": "world"}]


def test_call_step_with_empty_context(g):
    g.add_vertex("node")
    result = g.traversal().V().call("echo", {}).to_list()  # AttributeError
    assert result == [{}]


def test_call_step_unknown_service_raises(g):
    g.add_vertex("node")
    with pytest.raises(Exception):
        g.traversal().V().call("nonexistent_service", {}).to_list()  # AttributeError or ValueError


def test_call_step_uppercase_service(g):
    g.add_vertex("person", name="alice")
    result = g.traversal().V().call("uppercase", {"msg": "hello"}).to_list()  # AttributeError
    assert result[0]["msg"] == "HELLO"


def test_call_step_receives_traverser_context(g):
    v = g.add_vertex("person", name="Alice")
    ctx = {"_traverser": v.id, "mode": "test"}
    result = g.traversal().V().has("name", "Alice").call("capture", ctx).to_list()  # AttributeError
    assert len(result) == 1
    assert result[0]["_traverser"] == v.id


def test_call_step_only_affects_strings_in_context(g):
    g.add_vertex("person")
    result = g.traversal().V().call("uppercase", {"name": "alice", "age": 30}).to_list()  # AttributeError
    assert result[0]["name"] == "ALICE"
    assert result[0]["age"] == 30


def test_call_step_services_are_independent(g):
    g.add_vertex("node")
    echo_r = g.traversal().V().call("echo", {"msg": "hello"}).to_list()  # AttributeError
    upper_r = g.traversal().V().call("uppercase", {"msg": "hello"}).to_list()  # AttributeError
    assert echo_r[0]["msg"] == "hello"
    assert upper_r[0]["msg"] == "HELLO"


def test_call_step_with_inner_traversal(g):
    g.add_vertex("person", name="Alice")
    result = (
        g.traversal().V()
        .has_label("person")
        .call("echo", {}, g.traversal().V().has_label("person"))  # AttributeError
        .to_list()
    )
    assert isinstance(result, list)


def test_call_step_registers_multiple_services(g):
    g.add_vertex("item")
    services = ["svc_a", "svc_b"]
    for svc in services:
        result = g.traversal().V().call(svc, {"key": "value"}).to_list()  # AttributeError
        assert isinstance(result, list)
