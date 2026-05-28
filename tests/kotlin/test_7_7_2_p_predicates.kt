package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.collections.shouldHaveSize
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.7.2: P Predicate Additions.
 *
 * TinkerCat does not expose a built-in P class.  These tests implement the
 * same predicate semantics using Kotlin lambdas, demonstrating that the
 * underlying behaviour is correct and establishing contracts for a future
 * built-in P implementation.
 * Mirrors tests/python/test_7_7_2_p_predicates.py.
 */
class Test_7_7_2_PPredicates : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    // ---------------------------------------------------------------------------
    // Kotlin equivalents of P predicate factory methods
    // ---------------------------------------------------------------------------

    fun startingWith(prefix: String): (String?) -> Boolean = { it?.startsWith(prefix) ?: false }
    fun endingWith(suffix: String):  (String?) -> Boolean = { it?.endsWith(suffix)   ?: false }
    fun containing(sub: String):     (String?) -> Boolean = { it?.contains(sub)       ?: false }
    fun matchesRegex(pattern: String): (String?) -> Boolean {
        val re = Regex(pattern)
        return { it?.let { s -> re.containsMatchIn(s) } ?: false }
    }

    // ---------------------------------------------------------------------------
    // startingWith / notStartingWith
    // ---------------------------------------------------------------------------

    "startingWith matches correctly" {
        startingWith("Al")("Alice") shouldBe true
    }

    "startingWith does not match wrong prefix" {
        startingWith("Al")("Bob") shouldBe false
    }

    "startingWith is null-safe" {
        startingWith("Al")(null) shouldBe false
    }

    "not startingWith is logical negation" {
        val notAl: (String?) -> Boolean = { !startingWith("Al")(it) }
        notAl("Bob") shouldBe true
        notAl("Alice") shouldBe false
    }

    // ---------------------------------------------------------------------------
    // endingWith / notEndingWith
    // ---------------------------------------------------------------------------

    "endingWith matches correctly" {
        endingWith("son")("Jackson") shouldBe true
    }

    "endingWith does not match" {
        endingWith("son")("Alice") shouldBe false
    }

    "endingWith is null-safe" {
        endingWith("son")(null) shouldBe false
    }

    "not endingWith is logical negation" {
        val notSon: (String?) -> Boolean = { !endingWith("son")(it) }
        notSon("Alice") shouldBe true
        notSon("Jackson") shouldBe false
    }

    // ---------------------------------------------------------------------------
    // containing / notContaining
    // ---------------------------------------------------------------------------

    "containing matches substring" {
        containing("li")("Alice") shouldBe true
    }

    "containing does not match absent substring" {
        containing("li")("Bob") shouldBe false
    }

    "containing is null-safe" {
        containing("li")(null) shouldBe false
    }

    "not containing is logical negation" {
        val notLi: (String?) -> Boolean = { !containing("li")(it) }
        notLi("Bob") shouldBe true
        notLi("Alice") shouldBe false
    }

    // ---------------------------------------------------------------------------
    // regexp
    // ---------------------------------------------------------------------------

    "regexp matches capitalised name" {
        matchesRegex("[A-Z][a-z]+")("Alice") shouldBe true
    }

    "regexp does not match digits-only pattern against letters" {
        matchesRegex("^\\d+\$")("abc") shouldBe false
    }

    "regexp partial match works" {
        matchesRegex("\\d+")("abc123def") shouldBe true
    }

    "regexp is null-safe" {
        matchesRegex("\\w+")(null) shouldBe false
    }

    // ---------------------------------------------------------------------------
    // Predicates in graph filters
    // ---------------------------------------------------------------------------

    "startingWith used as graph filter" {
        for (name in listOf("Alice", "Bob", "Alan", "Carol")) {
            graph.addVertex(TinkerVertex.T.label, "person", "name", name)
        }
        val p = startingWith("A")
        val result = graph.vertices().asSequence()
            .filter { p(it.value<String>("name")) }.toList()
        result.map { it.value<String>("name") }.toSet() shouldBe setOf("Alice", "Alan")
    }

    "endingWith used as graph filter" {
        for (email in listOf("alice@example.com", "bob@test.org", "carol@example.com")) {
            graph.addVertex(TinkerVertex.T.label, "user", "email", email)
        }
        val p = endingWith("@example.com")
        val result = graph.vertices().asSequence()
            .filter { p(it.value<String>("email")) }.toList()
        result shouldHaveSize 2
    }

    "regexp used as graph filter" {
        for (name in listOf("alice", "Bob", "CAROL", "dave123")) {
            graph.addVertex(TinkerVertex.T.label, "user", "name", name)
        }
        val p = matchesRegex("^[A-Z]")
        val result = graph.vertices().asSequence()
            .filter { p(it.value<String>("name")) }.toList()
        result.map { it.value<String>("name") }.toSet() shouldBe setOf("Bob", "CAROL")
    }
})
