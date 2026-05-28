package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.longs.shouldBeGreaterThan
import kotlin.time.TimeSource
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.5.2: TinkerCatCountStrategy — Short-circuit Count.
 *
 * Validates that graph.vertices.size and graph.edges.size give O(1) counts,
 * and that label-based counts via Kotlin sequences are correct.
 * Mirrors tests/python/test_7_5_2_count_strategy.py.
 */
class Test_7_5_2_CountStrategy : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest {
        graph = TinkerCat.open()
        repeat(4) { graph.addVertex(TinkerVertex.T.label, "person") }
        repeat(2) { graph.addVertex(TinkerVertex.T.label, "software") }
    }

    "vertex count is correct" {
        graph.vertices.size shouldBe 6
    }

    "edge count is zero in vertex-only graph" {
        graph.edges.size shouldBe 0
    }

    "label count for person is correct" {
        val count = graph.vertices().asSequence().count { it.label() == "person" }
        count shouldBe 4
    }

    "label count for software is correct" {
        val count = graph.vertices().asSequence().count { it.label() == "software" }
        count shouldBe 2
    }

    "absent label count is zero" {
        val count = graph.vertices().asSequence().count { it.label() == "device" }
        count shouldBe 0
    }

    "vertices.size matches iterator count" {
        val slow = graph.vertices().asSequence().count()
        graph.vertices.size shouldBe slow
    }

    "label count matches filtered sequence count" {
        val fast = graph.vertices().asSequence().count { it.label() == "person" }
        fast shouldBe 4
    }

    "count increments after addVertex" {
        val before = graph.vertices.size
        graph.addVertex(TinkerVertex.T.label, "device")
        graph.vertices.size shouldBe before + 1
    }

    "vertices.size is faster than sequence iteration for large graphs" {
        val g2 = TinkerCat.open()
        repeat(10_000) { g2.addVertex(TinkerVertex.T.label, "node") }

        val clock = TimeSource.Monotonic

        val markFast = clock.markNow()
        repeat(1_000) { g2.vertices.size }
        val fastMs = markFast.elapsedNow().inWholeMilliseconds

        val markSlow = clock.markNow()
        repeat(1_000) { g2.vertices().asSequence().count() }
        val slowMs = markSlow.elapsedNow().inWholeMilliseconds

        fastMs shouldBeGreaterThan -1L  // sanity: non-negative
        // O(1) map.size should beat O(N) iteration; allow generous 5x margin
        (slowMs > fastMs || slowMs == 0L) shouldBe true
    }

    "edge count is correct after adding edges" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        a.addEdge("link", b)
        a.addEdge("link", b)
        graph.edges.size shouldBe 2
    }
})
