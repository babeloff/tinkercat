package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.8.1: Type Conversion Traversal Steps.
 *
 * Covers asBool() and asNumber() steps added in TinkerPop 3.8.0.
 * Mirrors tests/python/test_7_8_1_type_conversion_steps.py.
 */
class Test_7_8_1_TypeConversionSteps : StringSpec({

    // ── asBool ────────────────────────────────────────────────────────────────

    "asBool passthrough for Boolean true" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", true)
            val result = g.traversal().V().values<Boolean>("v").asBool().toList()
            result shouldBe listOf(true)
        } finally { g.close() }
    }

    "asBool passthrough for Boolean false" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", false)
            val result = g.traversal().V().values<Boolean>("v").asBool().toList()
            result shouldBe listOf(false)
        } finally { g.close() }
    }

    "asBool from String 'true'" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "true")
            val result = g.traversal().V().values<String>("v").asBool().toList()
            result shouldBe listOf(true)
        } finally { g.close() }
    }

    "asBool from String 'TRUE' is case-insensitive" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "TRUE")
            val result = g.traversal().V().values<String>("v").asBool().toList()
            result shouldBe listOf(true)
        } finally { g.close() }
    }

    "asBool from String 'false'" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "false")
            val result = g.traversal().V().values<String>("v").asBool().toList()
            result shouldBe listOf(false)
        } finally { g.close() }
    }

    "asBool from String '1' is true" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "1")
            val result = g.traversal().V().values<String>("v").asBool().toList()
            result shouldBe listOf(true)
        } finally { g.close() }
    }

    "asBool from String '0' is false" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "0")
            val result = g.traversal().V().values<String>("v").asBool().toList()
            result shouldBe listOf(false)
        } finally { g.close() }
    }

    "asBool from non-zero Int is true" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 42)
            val result = g.traversal().V().values<Int>("v").asBool().toList()
            result shouldBe listOf(true)
        } finally { g.close() }
    }

    "asBool from zero Int is false" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 0)
            val result = g.traversal().V().values<Int>("v").asBool().toList()
            result shouldBe listOf(false)
        } finally { g.close() }
    }

    "asBool from unsupported type raises" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", listOf(1, 2, 3))
            val caught = runCatching {
                g.traversal().V().values<Any>("v").asBool().toList()
            }.exceptionOrNull()
            (caught != null) shouldBe true
        } finally { g.close() }
    }

    // ── asNumber ──────────────────────────────────────────────────────────────

    "asNumber passthrough for Int" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 42)
            val result = g.traversal().V().values<Int>("v").asNumber().toList()
            result shouldBe listOf(42)
        } finally { g.close() }
    }

    "asNumber passthrough for Double" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 3.14)
            val result = g.traversal().V().values<Double>("v").asNumber().toList()
            result shouldBe listOf(3.14)
        } finally { g.close() }
    }

    "asNumber from String integer returns Long" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "100")
            val result = g.traversal().V().values<String>("v").asNumber().toList()
            result.first() shouldBe 100L
        } finally { g.close() }
    }

    "asNumber from String float returns Double" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "2.718")
            val result = g.traversal().V().values<String>("v").asNumber().toList()
            (result.first() as Double) shouldBe 2.718
        } finally { g.close() }
    }

    "asNumber from Boolean true is 1L" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", true)
            val result = g.traversal().V().values<Boolean>("v").asNumber().toList()
            result shouldBe listOf(1L)
        } finally { g.close() }
    }

    "asNumber from Boolean false is 0L" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", false)
            val result = g.traversal().V().values<Boolean>("v").asNumber().toList()
            result shouldBe listOf(0L)
        } finally { g.close() }
    }

    "asNumber from unparseable String raises" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", "not-a-number")
            val caught = runCatching {
                g.traversal().V().values<String>("v").asNumber().toList()
            }.exceptionOrNull()
            (caught != null) shouldBe true
        } finally { g.close() }
    }

    "asNumber from unsupported type raises" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", listOf(1))
            val caught = runCatching {
                g.traversal().V().values<Any>("v").asNumber().toList()
            }.exceptionOrNull()
            (caught != null) shouldBe true
        } finally { g.close() }
    }

    // ── pipeline composition ──────────────────────────────────────────────────

    "asNumber then comparison pipeline" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "score", "95")
            val result = g.traversal().V().values<String>("score").asNumber().toList()
            result.size shouldBe 1
            result.first() shouldBe 95L
        } finally { g.close() }
    }
})
