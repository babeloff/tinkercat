package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.types.shouldBeInstanceOf
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerTransaction
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.2.1: TinkerTransactionGraph — ACID Transaction Support.
 *
 * TinkerCat.tx() returns a TinkerTransaction stub whose every method throws
 * UnsupportedOperationException. Tests marked "!" are pending until a real
 * transaction implementation lands; their bodies compile because TinkerTransaction
 * is defined in source (not just in this test).
 * Mirrors tests/python/test_7_2_1_transaction_graph.py.
 */
class Test_7_2_1_TransactionGraph : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    "tx() returns a TinkerTransaction stub" {
        val tx = graph.tx()
        tx.shouldBeInstanceOf<TinkerTransaction>()
    }

    "tx().open() raises UnsupportedOperationException — not yet implemented" {
        val tx = graph.tx()
        val caught = runCatching { tx.open() }.exceptionOrNull()
        (caught is UnsupportedOperationException) shouldBe true
    }

    "!commit persists changes" {
        val tx = graph.tx()
        tx.open()
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        tx.commit()
        graph.vertices.size shouldBe 1
    }

    "!rollback reverts changes" {
        val tx = graph.tx()
        tx.open()
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        tx.rollback()
        graph.vertices.size shouldBe 0
    }

    "!double open raises" {
        val tx = graph.tx()
        tx.open()
        runCatching { tx.open() }.isFailure shouldBe true
        tx.rollback()
    }

    "!commit without open raises" {
        val tx = graph.tx()
        runCatching { tx.commit() }.isFailure shouldBe true
    }

    "!rollback without open raises" {
        val tx = graph.tx()
        runCatching { tx.rollback() }.isFailure shouldBe true
    }

    "!context manager commits on success" {
        graph.tx().use { tx ->
            tx.open()
            graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        }
        graph.vertices.size shouldBe 1
    }

    "!context manager rolls back on exception" {
        runCatching {
            graph.tx().use { tx ->
                tx.open()
                graph.addVertex(TinkerVertex.T.label, "person")
                throw RuntimeException("deliberate error")
            }
        }
        graph.vertices.size shouldBe 0
    }

    "!rollback restores property values" {
        val v = graph.addVertex(TinkerVertex.T.label, "item", "score", 10) as TinkerVertex
        val tx = graph.tx()
        tx.open()
        v.property("score", 99)
        tx.rollback()
        v.value<Int>("score") shouldBe 10
    }

    "!committed changes survive new rollback" {
        graph.tx().use { tx ->
            tx.open()
            graph.addVertex(TinkerVertex.T.label, "node")
        }
        val tx2 = graph.tx()
        tx2.open()
        graph.addVertex(TinkerVertex.T.label, "node")
        tx2.rollback()
        graph.vertices.size shouldBe 1
    }
})
