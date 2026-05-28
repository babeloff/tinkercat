package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import org.apache.tinkerpop.gremlin.structure.Vertex
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.4.1: mergeV() and mergeE() Upsert Steps.
 *
 * TinkerCat's Kotlin API does not expose built-in mergeV/mergeE methods.
 * These tests implement the upsert semantics inline with Kotlin sequences
 * and verify the behaviour is correct — establishing what a future built-in
 * implementation must satisfy.
 * Mirrors tests/python/test_7_4_1_merge_steps.py.
 */
class Test_7_4_1_MergeSteps : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    // ---------------------------------------------------------------------------
    // Inline mergeV / mergeE helpers (no TinkerCat built-in yet)
    // ---------------------------------------------------------------------------

    fun mergeV(
        label: String,
        criteria: Map<String, Any?>,
        onCreate: Map<String, Any?> = criteria,
        onMatch: Map<String, Any?> = emptyMap(),
    ): Vertex {
        val candidate = graph.vertices().asSequence()
            .filter { it.label() == label }
            .filter { criteria.all { (k, v) -> it.value<Any?>(k) == v } }
            .firstOrNull()
        return if (candidate != null) {
            onMatch.forEach { (k, v) -> (candidate as TinkerVertex).property(k, v) }
            candidate
        } else {
            val args = mutableListOf<Any?>(TinkerVertex.T.label, label)
            onCreate.forEach { (k, v) -> args += k; args += v }
            graph.addVertex(*args.toTypedArray())
        }
    }

    fun mergeE(
        label: String,
        outV: Vertex,
        inV: Vertex,
        criteria: Map<String, Any?> = emptyMap(),
        onMatch: Map<String, Any?> = emptyMap(),
    ) = graph.edges().asSequence()
        .filter { it.label() == label && it.outVertex().id() == outV.id() && it.inVertex().id() == inV.id() }
        .filter { criteria.all { (k, v) -> it.value<Any?>(k) == v } }
        .firstOrNull()
        ?.also { e -> onMatch.forEach { (k, v) -> e.property(k, v) } }
        ?: run {
            val args = mutableListOf<Any?>()
            criteria.forEach { (k, v) -> args += k; args += v }
            outV.addEdge(label, inV, *args.toTypedArray())
        }

    // ---------------------------------------------------------------------------
    // mergeV tests
    // ---------------------------------------------------------------------------

    "merge_v creates vertex when none matches" {
        val v = mergeV("person", mapOf("email" to "alice@example.com"),
            onCreate = mapOf("email" to "alice@example.com", "created" to true))
        graph.vertices.size shouldBe 1
        v.value<String>("email") shouldBe "alice@example.com"
        v.value<Boolean>("created") shouldBe true
    }

    "merge_v matches existing vertex without duplication" {
        val existing = graph.addVertex(TinkerVertex.T.label, "person",
            "email", "alice@example.com", "lastSeen", "old") as TinkerVertex
        mergeV("person", mapOf("email" to "alice@example.com"),
            onMatch = mapOf("lastSeen" to "new"))
        graph.vertices.size shouldBe 1
        existing.value<String>("lastSeen") shouldBe "new"
    }

    "merge_v with no on_create uses search criteria" {
        val v = mergeV("person", mapOf("name" to "Bob"))
        v.value<String>("name") shouldBe "Bob"
    }

    "merge_v with no on_match returns vertex unchanged" {
        graph.addVertex(TinkerVertex.T.label, "person", "email", "x@y.com", "score", 10)
        val v = mergeV("person", mapOf("email" to "x@y.com"))
        v.value<Int>("score") shouldBe 10
    }

    "merge_v is idempotent" {
        val criteria = mapOf("email" to "alice@example.com")
        mergeV("person", criteria)
        mergeV("person", criteria)
        graph.vertices.size shouldBe 1
    }

    // ---------------------------------------------------------------------------
    // mergeE tests
    // ---------------------------------------------------------------------------

    "merge_e creates edge when none exists" {
        val a = graph.addVertex(TinkerVertex.T.label, "person")
        val b = graph.addVertex(TinkerVertex.T.label, "person")
        mergeE("knows", a, b)
        graph.edges.size shouldBe 1
    }

    "merge_e matches existing edge without duplication" {
        val a = graph.addVertex(TinkerVertex.T.label, "person")
        val b = graph.addVertex(TinkerVertex.T.label, "person")
        a.addEdge("knows", b, "since", "2020")
        mergeE("knows", a, b, onMatch = mapOf("since" to "2024"))
        graph.edges.size shouldBe 1
        graph.edges().asSequence().first().value<String>("since") shouldBe "2024"
    }

    "merge_e is idempotent" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        mergeE("link", a, b)
        mergeE("link", a, b)
        graph.edges.size shouldBe 1
    }

    "merge_e result has correct label" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        val e = mergeE("likes", a, b)
        e.label() shouldBe "likes"
    }
})
