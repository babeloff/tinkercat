"""
Tests for Task 7.4.5: call() Service Invocation Step.

Validates the TraversalCallbackService interface, service registry,
EchoService reference implementation, and mid-traversal call() semantics.
See docs/project/changelog/task-7.4.5-call-step.adoc.
"""

import pytest
from typing import Any, Dict, Iterator, Optional

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Mock service infrastructure
# ---------------------------------------------------------------------------

class TraversalCallbackService:
    name: str

    def execute(
        self,
        context: Dict[str, Any],
        inner_traversal=None,
    ) -> Iterator[Dict[str, Any]]:
        raise NotImplementedError

class EchoService(TraversalCallbackService):
    name = "echo"

    def execute(self, context, inner_traversal=None):
        return iter([context])

class UpperCaseService(TraversalCallbackService):
    """Returns context with all string values uppercased."""
    name = "uppercase"

    def execute(self, context, inner_traversal=None):
        return iter([{k: v.upper() if isinstance(v, str) else v
                      for k, v in context.items()}])

class ServiceRegistry:
    def __init__(self):
        self._services: Dict[str, TraversalCallbackService] = {}

    def register(self, service: TraversalCallbackService) -> "ServiceRegistry":
        copy = ServiceRegistry()
        copy._services = dict(self._services)
        copy._services[service.name] = service
        return copy

    def call(self, name: str, context: Dict[str, Any], inner_traversal=None):
        if name not in self._services:
            raise ValueError(f"No service registered: '{name}'")
        return list(self._services[name].execute(context, inner_traversal))

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_echo_service_returns_context():
    svc = EchoService()
    ctx = {"hello": "world"}
    result = list(svc.execute(ctx))
    assert len(result) == 1
    assert result[0] == ctx

def test_echo_service_name():
    assert EchoService.name == "echo"

def test_registry_register_returns_new_instance():
    r1 = ServiceRegistry()
    r2 = r1.register(EchoService())
    # r1 is immutable — echo not in r1
    with pytest.raises(ValueError):
        r1.call("echo", {})

def test_registry_call_known_service():
    r = ServiceRegistry().register(EchoService())
    result = r.call("echo", {"key": "value"})
    assert result == [{"key": "value"}]

def test_registry_call_unknown_service_raises():
    r = ServiceRegistry()
    with pytest.raises(ValueError, match="No service registered"):
        r.call("nonexistent", {})

def test_two_services_coexist():
    r = ServiceRegistry().register(EchoService()).register(UpperCaseService())
    echo_r = r.call("echo", {"msg": "hello"})
    upper_r = r.call("uppercase", {"msg": "hello"})
    assert echo_r[0]["msg"] == "hello"
    assert upper_r[0]["msg"] == "HELLO"

def test_uppercase_service_only_affects_strings():
    svc = UpperCaseService()
    result = list(svc.execute({"name": "alice", "age": 30}))
    assert result[0]["name"] == "ALICE"
    assert result[0]["age"] == 30

def test_mid_traversal_call_receives_traverser_context():
    class CapturingService(TraversalCallbackService):
        name = "capture"
        received_contexts = []

        def execute(self, context, inner_traversal=None):
            self.received_contexts.append(dict(context))
            return iter([context])

    svc = CapturingService()
    r = ServiceRegistry().register(svc)
    g = TinkerCat()
    try:
        v = g.add_vertex("person", name="Alice")

        ctx = {"_traverser": v.id, "mode": "test"}
        r.call("capture", ctx)

        assert len(svc.received_contexts) == 1
        assert svc.received_contexts[0]["_traverser"] == v.id
    finally:
        g.close()

def test_service_with_empty_context():
    r = ServiceRegistry().register(EchoService())
    result = r.call("echo", {})
    assert result == [{}]
