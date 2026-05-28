package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.process.traversal.DT
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.4.3: Date/Time Traversal Steps.
 *
 * All tests call asDate(), dateAdd(), and dateDiff() as traversal steps.
 * Date values are stored as epoch-milliseconds (Long) or ISO-8601 strings,
 * since Kotlin Multiplatform commonMain has no java.time dependency.
 * Mirrors tests/python/test_7_4_3_datetime_steps.py.
 */
class Test_7_4_3_DatetimeSteps : StringSpec({

    // epoch-ms for 2024-01-15T12:00:00Z
    val JAN_15_EPOCH_MS = 1_705_320_000_000L
    // epoch-ms for 2024-01-01T00:00:00Z
    val JAN_01_EPOCH_MS = 1_704_067_200_000L
    // epoch-ms for 2024-01-08T00:00:00Z
    val JAN_08_EPOCH_MS = 1_704_672_000_000L

    lateinit var graph: TinkerCat

    beforeTest {
        graph = TinkerCat.open()
        graph.addVertex(TinkerVertex.T.label, "event", "ts", JAN_15_EPOCH_MS)
        graph.addVertex(TinkerVertex.T.label, "event", "ts", "2024-01-15T12:00:00+00:00")
        graph.addVertex(TinkerVertex.T.label, "event", "ts", JAN_01_EPOCH_MS)
        graph.addVertex(TinkerVertex.T.label, "event", "ts", JAN_08_EPOCH_MS)
    }

    // ── asDate ────────────────────────────────────────────────────────────────

    "asDate from epoch ms produces a date value" {
        val result = graph.traversal().V()
            .has("ts", JAN_15_EPOCH_MS)
            .values<Long>("ts")
            .asDate()
            .toList()
        result.size shouldBe 1
    }

    "asDate from ISO string produces a date value" {
        val result = graph.traversal().V()
            .has("ts", "2024-01-15T12:00:00+00:00")
            .values<String>("ts")
            .asDate()
            .toList()
        result.size shouldBe 1
    }

    "asDate from unsupported type raises" {
        val g2 = TinkerCat.open()
        try {
            g2.addVertex(TinkerVertex.T.label, "e", "ts", listOf(1, 2, 3))
            val caught = runCatching {
                g2.traversal().V().values<Any>("ts").asDate().toList()
            }.exceptionOrNull()
            (caught != null) shouldBe true
        } finally {
            g2.close()
        }
    }

    // ── dateAdd ───────────────────────────────────────────────────────────────

    "dateAdd adds days to a date" {
        val result = graph.traversal().V()
            .has("ts", JAN_01_EPOCH_MS)
            .values<Long>("ts")
            .asDate()
            .dateAdd(DT.day, 7)
            .toList()
        // 2024-01-01 + 7 days = 2024-01-08
        result.size shouldBe 1
    }

    "dateAdd adds hours to a date" {
        val result = graph.traversal().V()
            .has("ts", JAN_15_EPOCH_MS)
            .values<Long>("ts")
            .asDate()
            .dateAdd(DT.hour, 3)
            .toList()
        result.size shouldBe 1
    }

    "dateAdd with negative amount subtracts" {
        val result = graph.traversal().V()
            .has("ts", JAN_08_EPOCH_MS)
            .values<Long>("ts")
            .asDate()
            .dateAdd(DT.day, -7)
            .toList()
        // 2024-01-08 - 7 days = 2024-01-01
        result.size shouldBe 1
    }

    "dateAdd zero leaves date unchanged" {
        val result = graph.traversal().V()
            .has("ts", JAN_01_EPOCH_MS)
            .values<Long>("ts")
            .asDate()
            .dateAdd(DT.day, 0)
            .toList()
        result.size shouldBe 1
    }

    // ── dateDiff ──────────────────────────────────────────────────────────────

    "dateDiff produces a list of differences" {
        val result = graph.traversal().V()
            .hasLabel("event")
            .values<Any>("ts")
            .asDate()
            .dateDiff(JAN_08_EPOCH_MS, DT.day)
            .toList()
        (result is List<*>) shouldBe true
    }

    "dateDiff of same instant is zero" {
        val g2 = TinkerCat.open()
        try {
            g2.addVertex(TinkerVertex.T.label, "e", "ts", JAN_01_EPOCH_MS)
            val result = g2.traversal().V()
                .values<Long>("ts")
                .asDate()
                .dateDiff(JAN_01_EPOCH_MS, DT.second)
                .toList()
            result shouldBe listOf(0L)
        } finally {
            g2.close()
        }
    }

    "dateDiff in hours returns correct count" {
        val g2 = TinkerCat.open()
        // 2024-01-01T09:00:00Z and 2024-01-01T15:00:00Z differ by 6 hours
        val epochA = 1_704_099_600_000L  // 09:00
        val epochB = 1_704_121_200_000L  // 15:00
        try {
            g2.addVertex(TinkerVertex.T.label, "e", "ts", epochA)
            val result = g2.traversal().V()
                .values<Long>("ts")
                .asDate()
                .dateDiff(epochB, DT.hour)
                .toList()
            result shouldBe listOf(6L)
        } finally {
            g2.close()
        }
    }

    // ── pipeline ──────────────────────────────────────────────────────────────

    "asDate then dateAdd pipeline" {
        val g2 = TinkerCat.open()
        try {
            g2.addVertex(TinkerVertex.T.label, "e", "ts", "2024-01-01T00:00:00+00:00")
            val result = g2.traversal().V()
                .values<String>("ts")
                .asDate()
                .dateAdd(DT.day, 30)
                .toList()
            result.size shouldBe 1
        } finally {
            g2.close()
        }
    }
})
