package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant
import kotlinx.datetime.LocalDate
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex
import kotlin.time.Duration.Companion.days
import kotlin.time.Duration.Companion.hours

/**
 * Tests for Task 7.3.1: Temporal Property Value Support.
 *
 * TinkerCat stores any Kotlin object as a property value, so kotlinx.datetime
 * types work directly.  All tests pass because the storage layer is untyped.
 * Mirrors tests/python/test_7_3_1_temporal_properties.py.
 */
class Test_7_3_1_TemporalProperties : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    "store and retrieve an Instant property" {
        val now = Clock.System.now()
        val v = graph.addVertex(TinkerVertex.T.label, "event") as TinkerVertex
        v.property("ts", now)
        v.value<Instant>("ts") shouldBe now
    }

    "instant comparison is preserved" {
        val t1 = Instant.parse("2024-01-01T00:00:00Z")
        val t2 = Instant.parse("2024-06-01T00:00:00Z")
        (t1 < t2) shouldBe true
        (t2 > t1) shouldBe true
    }

    "instant from epoch milliseconds round-trips" {
        val ms = 1_700_000_000_000L
        val instant = Instant.fromEpochMilliseconds(ms)
        instant.toEpochMilliseconds() shouldBe ms
    }

    "instant parse from ISO-8601 string" {
        val instant = Instant.parse("2024-01-15T12:00:00Z")
        val ldt = instant.toLocalDateTime(TimeZone.UTC)
        ldt.year shouldBe 2024
        ldt.monthNumber shouldBe 1
        ldt.dayOfMonth shouldBe 15
    }

    "store and retrieve a LocalDate property" {
        val d = LocalDate(2024, 6, 1)
        val v = graph.addVertex(TinkerVertex.T.label, "log") as TinkerVertex
        v.property("date", d)
        v.value<LocalDate>("date") shouldBe d
    }

    "local date ordering is correct" {
        val d1 = LocalDate(2023, 1, 1)
        val d2 = LocalDate(2024, 1, 1)
        (d1 < d2) shouldBe true
    }

    "store and retrieve a Duration property" {
        val dur = 7.days
        val v = graph.addVertex(TinkerVertex.T.label, "task") as TinkerVertex
        v.property("duration", dur)
        v.value<kotlin.time.Duration>("duration") shouldBe dur
    }

    "range filter on instant properties" {
        val dates = listOf("2024-01-01T00:00:00Z", "2024-06-01T00:00:00Z", "2024-12-01T00:00:00Z")
        for (ds in dates) {
            val v = graph.addVertex(TinkerVertex.T.label, "event") as TinkerVertex
            v.property("ts", Instant.parse(ds))
        }
        val cutoff = Instant.parse("2024-07-01T00:00:00Z")
        val before = graph.vertices().asSequence()
            .filter { it.value<Instant>("ts") != null && it.value<Instant>("ts")!! < cutoff }
            .toList()
        before.size shouldBe 2
    }

    "absent temporal property returns null" {
        val v = graph.addVertex(TinkerVertex.T.label, "event")
        v.value<Instant>("ts") shouldBe null
    }

    "add duration to instant" {
        val base = Instant.parse("2024-01-01T00:00:00Z")
        val shifted = base + 7.days
        val ldt = shifted.toLocalDateTime(TimeZone.UTC)
        ldt.dayOfMonth shouldBe 8
    }

    "duration between two instants" {
        val a = Instant.parse("2024-01-01T00:00:00Z")
        val b = Instant.parse("2024-01-08T00:00:00Z")
        val diff = b - a
        diff shouldBe 7.days
    }
})
