package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.4.5: call() Service Invocation Step.
 *
 * All tests invoke the call() traversal step, which throws
 * UnsupportedOperationException until the service registry is implemented.
 * Mirrors tests/python/test_7_4_5_call_step.py.
 */
class Test_7_4_5_CallStep : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    "call echo service returns context unchanged" {
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        val result = graph.traversal().V()
            .call("echo", mapOf("hello" to "world"))
            .toList()
        result shouldBe listOf(mapOf("hello" to "world"))
    }

    "call with empty context returns empty map" {
        graph.addVertex(TinkerVertex.T.label, "node")
        val result = graph.traversal().V()
            .call("echo", emptyMap())
            .toList()
        result shouldBe listOf(emptyMap())
    }

    "call with unknown service name raises" {
        graph.addVertex(TinkerVertex.T.label, "node")
        val caught = runCatching {
            graph.traversal().V()
                .call("nonexistent_service", emptyMap())
                .toList()
        }.exceptionOrNull()
        (caught != null) shouldBe true
    }

    "call uppercase service transforms string values" {
        graph.addVertex(TinkerVertex.T.label, "person", "name", "alice")
        val result = graph.traversal().V()
            .call("uppercase", mapOf("msg" to "hello"))
            .toList()
        (result[0]["msg"] as String) shouldBe "HELLO"
    }

    "call step receives traverser context" {
        val v = graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        val ctx = mapOf("_traverser" to v.id(), "mode" to "test")
        val result = graph.traversal().V()
            .has("name", "Alice")
            .call("capture", ctx)
            .toList()
        result.size shouldBe 1
        result[0]["_traverser"] shouldBe v.id()
    }

    "call uppercase only affects string values" {
        graph.addVertex(TinkerVertex.T.label, "person")
        val result = graph.traversal().V()
            .call("uppercase", mapOf("name" to "alice", "age" to 30))
            .toList()
        (result[0]["name"] as String) shouldBe "ALICE"
        result[0]["age"] shouldBe 30
    }

    "echo and uppercase services are independent" {
        graph.addVertex(TinkerVertex.T.label, "node")
        val echoResult = graph.traversal().V()
            .call("echo", mapOf("msg" to "hello")).toList()
        val upperResult = graph.traversal().V()
            .call("uppercase", mapOf("msg" to "hello")).toList()
        echoResult[0]["msg"] shouldBe "hello"
        (upperResult[0]["msg"] as String) shouldBe "HELLO"
    }

    "call with inner traversal argument" {
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        val result = graph.traversal().V()
            .hasLabel("person")
            .call("echo", emptyMap(), graph.traversal().V().hasLabel("person"))
            .toList()
        (result is List<*>) shouldBe true
    }

    "call registers multiple services independently" {
        graph.addVertex(TinkerVertex.T.label, "item")
        for (svc in listOf("svc_a", "svc_b")) {
            val result = graph.traversal().V()
                .call(svc, mapOf("key" to "value"))
                .toList()
            (result is List<*>) shouldBe true
        }
    }
})
