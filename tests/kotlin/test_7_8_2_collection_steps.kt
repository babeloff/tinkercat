package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.process.traversal.P
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.8.2: Collection / Set Traversal Steps.
 *
 * Covers all(), any() (implemented) and the unimplemented stubs:
 * difference, disjunct, intersect, conjoin, combine, product, merge.
 * Mirrors tests/python/test_7_8_2_collection_steps.py.
 */
class Test_7_8_2_CollectionSteps : StringSpec({

    // ── all ───────────────────────────────────────────────────────────────────

    "all keeps scalar that satisfies predicate" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "score", 10)
            val result = g.traversal().V().values<Int>("score").all(P.gt(5)).toList()
            result.size shouldBe 1
        } finally { g.close() }
    }

    "all removes scalar that does not satisfy predicate" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "score", 3)
            val result = g.traversal().V().values<Int>("score").all(P.gt(5)).toList()
            result.size shouldBe 0
        } finally { g.close() }
    }

    "all keeps list when every element passes" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(5, 6, 7))
            val result = g.traversal().V().values<Any>("nums").all(P.gt(3)).toList()
            result.size shouldBe 1
        } finally { g.close() }
    }

    "all removes list when any element fails" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(5, 6, 2))
            val result = g.traversal().V().values<Any>("nums").all(P.gt(3)).toList()
            result.size shouldBe 0
        } finally { g.close() }
    }

    "all on mixed vertices keeps only those where all elements pass" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(10, 20, 30))
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(10, 20,  2))
            val result = g.traversal().V().values<Any>("nums").all(P.gt(5)).toList()
            result.size shouldBe 1
        } finally { g.close() }
    }

    // ── any ───────────────────────────────────────────────────────────────────

    "any keeps scalar that satisfies predicate" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "score", 10)
            val result = g.traversal().V().values<Int>("score").any(P.gt(5)).toList()
            result.size shouldBe 1
        } finally { g.close() }
    }

    "any removes scalar that does not satisfy predicate" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "score", 3)
            val result = g.traversal().V().values<Int>("score").any(P.gt(5)).toList()
            result.size shouldBe 0
        } finally { g.close() }
    }

    "any keeps list when at least one element passes" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(1, 2, 10))
            val result = g.traversal().V().values<Any>("nums").any(P.gt(5)).toList()
            result.size shouldBe 1
        } finally { g.close() }
    }

    "any removes list when no element passes" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(1, 2, 3))
            val result = g.traversal().V().values<Any>("nums").any(P.gt(5)).toList()
            result.size shouldBe 0
        } finally { g.close() }
    }

    "any on mixed vertices returns only matching" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(1, 2, 10))
            g.addVertex(TinkerVertex.T.label, "e", "nums", listOf(1, 2,  3))
            val result = g.traversal().V().values<Any>("nums").any(P.gt(5)).toList()
            result.size shouldBe 1
        } finally { g.close() }
    }

    // ── unimplemented stubs ───────────────────────────────────────────────────

    "difference throws UnsupportedOperationException" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 1)
            val caught = runCatching {
                g.traversal().V().values<Int>("v").difference(setOf(1)).toList()
            }.exceptionOrNull()
            (caught is UnsupportedOperationException) shouldBe true
        } finally { g.close() }
    }

    "disjunct throws UnsupportedOperationException" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 1)
            val caught = runCatching {
                g.traversal().V().values<Int>("v").disjunct(setOf(1)).toList()
            }.exceptionOrNull()
            (caught is UnsupportedOperationException) shouldBe true
        } finally { g.close() }
    }

    "intersect throws UnsupportedOperationException" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 1)
            val caught = runCatching {
                g.traversal().V().values<Int>("v").intersect(setOf(1)).toList()
            }.exceptionOrNull()
            (caught is UnsupportedOperationException) shouldBe true
        } finally { g.close() }
    }

    "conjoin throws UnsupportedOperationException" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 1)
            val caught = runCatching {
                g.traversal().V().values<Int>("v").conjoin(",").toList()
            }.exceptionOrNull()
            (caught is UnsupportedOperationException) shouldBe true
        } finally { g.close() }
    }

    "combine throws UnsupportedOperationException" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 1)
            val caught = runCatching {
                g.traversal().V().values<Int>("v").combine(listOf(1)).toList()
            }.exceptionOrNull()
            (caught is UnsupportedOperationException) shouldBe true
        } finally { g.close() }
    }

    "product throws UnsupportedOperationException" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 1)
            val caught = runCatching {
                g.traversal().V().values<Int>("v").product(listOf(1)).toList()
            }.exceptionOrNull()
            (caught is UnsupportedOperationException) shouldBe true
        } finally { g.close() }
    }

    "merge throws UnsupportedOperationException" {
        val g = TinkerCat.open()
        try {
            g.addVertex(TinkerVertex.T.label, "e", "v", 1)
            val caught = runCatching {
                g.traversal().V().values<Int>("v").merge(mapOf("a" to 1)).toList()
            }.exceptionOrNull()
            (caught is UnsupportedOperationException) shouldBe true
        } finally { g.close() }
    }
})
