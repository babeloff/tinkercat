package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 2.2.1: Multi-Property Support.
 *
 * Validates that vertices and edges can carry multiple properties of various
 * types, that properties can be read back without loss, and that absent
 * properties return null.
 * Mirrors tests/python/test_2_2_1_multi_property_support.py.
 */
class Test_2_2_1_MultiPropertySupport : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    "vertex can store a string property" {
        val v = graph.addVertex(TinkerVertex.T.label, "item", "name", "Widget")
        v.value<String>("name") shouldBe "Widget"
    }

    "vertex can store an integer property" {
        val v = graph.addVertex(TinkerVertex.T.label, "item", "count", 42)
        v.value<Int>("count") shouldBe 42
    }

    "vertex can store a long property" {
        val v = graph.addVertex(TinkerVertex.T.label, "item", "big", 9_000_000_000L)
        v.value<Long>("big") shouldBe 9_000_000_000L
    }

    "vertex can store a double property" {
        val v = graph.addVertex(TinkerVertex.T.label, "item", "price", 3.14)
        v.value<Double>("price") shouldBe 3.14
    }

    "vertex can store a boolean property" {
        val v = graph.addVertex(TinkerVertex.T.label, "flag", "active", true)
        v.value<Boolean>("active") shouldBe true
    }

    "vertex can carry multiple properties simultaneously" {
        val v = graph.addVertex(
            TinkerVertex.T.label, "person",
            "name", "Alice",
            "age", 30,
            "active", true,
            "score", 9.5
        )
        v.value<String>("name") shouldBe "Alice"
        v.value<Int>("age") shouldBe 30
        v.value<Boolean>("active") shouldBe true
        v.value<Double>("score") shouldBe 9.5
    }

    "absent property returns null" {
        val v = graph.addVertex(TinkerVertex.T.label, "item", "name", "X")
        v.value<String>("missing") shouldBe null
    }

    "property set via property() is readable via value()" {
        val v = graph.addVertex(TinkerVertex.T.label, "item") as TinkerVertex
        v.property("score", 99)
        v.value<Int>("score") shouldBe 99
    }

    "property update overwrites previous value" {
        val v = graph.addVertex(TinkerVertex.T.label, "item") as TinkerVertex
        v.property("score", 10)
        v.property("score", 20)
        v.value<Int>("score") shouldBe 20
    }

    "edge can carry properties" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        val e = a.addEdge("knows", b, "since", 2020, "weight", 0.8)
        e.value<Int>("since") shouldBe 2020
        e.value<Double>("weight") shouldBe 0.8
    }

    "edge property set separately is readable" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        val e = a.addEdge("link", b)
        e.property("tag", "important")
        e.value<String>("tag") shouldBe "important"
    }

    "distinct vertices with same property key are independent" {
        val v1 = graph.addVertex(TinkerVertex.T.label, "item", "x", 1)
        val v2 = graph.addVertex(TinkerVertex.T.label, "item", "x", 2)
        v1.value<Int>("x") shouldBe 1
        v2.value<Int>("x") shouldBe 2
    }

    "property key is case-sensitive" {
        val v = graph.addVertex(TinkerVertex.T.label, "item", "Name", "Alice")
        v.value<String>("Name") shouldBe "Alice"
        v.value<String>("name") shouldBe null
    }
})
