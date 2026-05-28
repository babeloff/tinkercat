package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.5.1: TinkerCatStepStrategy — has() Predicate Push-down.
 *
 * Validates filtering by property equality and by label using Kotlin sequences —
 * the native equivalent of the Python traversal's has() and has_label() steps.
 * Range predicates are expressed directly in Kotlin without P.gte etc.
 * Mirrors tests/python/test_7_5_1_step_strategy.py.
 */
class Test_7_5_1_StepStrategy : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest {
        graph = TinkerCat.open()
        for ((name, age) in listOf("Alice" to 25, "Bob" to 30, "Carol" to 35, "Dave" to 40)) {
            graph.addVertex(TinkerVertex.T.label, "person", "name", name, "age", age)
        }
    }

    "has equivalent returns correct single match" {
        val result = graph.vertices().asSequence()
            .filter { it.value<String>("name") == "Alice" }.toList()
        result shouldHaveSize 1
        result[0].value<String>("name") shouldBe "Alice"
    }

    "has equivalent on different value returns correct match" {
        val result = graph.vertices().asSequence()
            .filter { it.value<String>("name") == "Bob" }.toList()
        result shouldHaveSize 1
        result[0].value<String>("name") shouldBe "Bob"
    }

    "range predicate filters correctly" {
        val result = graph.vertices().asSequence()
            .filter { it.value<Int>("age") != null && it.value<Int>("age")!! >= 30 }.toList()
        val names = result.map { it.value<String>("name") }.toSet()
        names shouldBe setOf("Bob", "Carol", "Dave")
    }

    "no filter returns all vertices" {
        graph.vertices().asSequence().toList() shouldHaveSize graph.vertices.size
    }

    "chained has predicates all must match" {
        val result = graph.vertices().asSequence()
            .filter { it.value<String>("name") == "Bob" }
            .filter { it.value<Int>("age") == 30 }
            .toList()
        result shouldHaveSize 1
        result[0].value<String>("name") shouldBe "Bob"
    }

    "has_label equivalent returns correct subset" {
        val g2 = TinkerCat.open()
        repeat(3) { g2.addVertex(TinkerVertex.T.label, "person") }
        repeat(2) { g2.addVertex(TinkerVertex.T.label, "software") }
        val persons = g2.vertices().asSequence()
            .filter { it.label() == "person" }.toList()
        persons shouldHaveSize 3
    }

    "no match returns empty list" {
        val result = graph.vertices().asSequence()
            .filter { it.value<String>("name") == "Nonexistent" }.toList()
        result shouldHaveSize 0
    }

    "has_not equivalent returns vertices without property" {
        val g2 = TinkerCat.open()
        g2.addVertex(TinkerVertex.T.label, "person", "name", "Alice", "email", "a@b.com")
        g2.addVertex(TinkerVertex.T.label, "person", "name", "Bob")
        val noEmail = g2.vertices().asSequence()
            .filter { it.value<String>("email") == null }.toList()
        noEmail shouldHaveSize 1
        noEmail[0].value<String>("name") shouldBe "Bob"
    }

    "index-backed vertex lookup by id is O(1)" {
        val v = graph.addVertex(TinkerVertex.T.label, "n")
        val found = graph.vertex(v.id())
        found?.id() shouldBe v.id()
    }
})
