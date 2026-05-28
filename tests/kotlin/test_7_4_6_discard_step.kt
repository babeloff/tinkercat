package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.4.6: discard() Step.
 *
 * All tests call the discard() traversal step.  discard() throws
 * UnsupportedOperationException until implemented; property() mutation step
 * throws the same exception.
 * Note: iterate() IS implemented and is used as a comparison baseline.
 * Mirrors tests/python/test_7_4_6_discard_step.py.
 */
class Test_7_4_6_DiscardStep : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest {
        graph = TinkerCat.open()
        val marko  = graph.addVertex(TinkerVertex.T.label, "person",   "name", "marko",  "age", 29)
        val vadas  = graph.addVertex(TinkerVertex.T.label, "person",   "name", "vadas",  "age", 27)
        val lop    = graph.addVertex(TinkerVertex.T.label, "software", "name", "lop",    "lang", "java")
        val josh   = graph.addVertex(TinkerVertex.T.label, "person",   "name", "josh",   "age", 32)
        val ripple = graph.addVertex(TinkerVertex.T.label, "software", "name", "ripple", "lang", "java")
        val peter  = graph.addVertex(TinkerVertex.T.label, "person",   "name", "peter",  "age", 35)

        marko.addEdge("knows",   vadas,  "weight", 0.5)
        marko.addEdge("knows",   josh,   "weight", 1.0)
        marko.addEdge("created", lop,    "weight", 0.4)
        josh.addEdge("created",  ripple, "weight", 1.0)
        josh.addEdge("created",  lop,    "weight", 0.4)
        peter.addEdge("created", lop,    "weight", 0.2)
    }

    "discard returns Unit without error" {
        graph.traversal().V().discard()
        // if we reach here with Unit return, the step is implemented
    }

    "discard on empty graph does not raise" {
        val g2 = TinkerCat.open()
        try {
            g2.traversal().V().discard()
        } finally {
            g2.close()
        }
    }

    "discard drains the pipeline" {
        val t = graph.traversal().V()
        t.discard()
        t.toList() shouldBe emptyList()
    }

    "side effects execute before discard" {
        val log = mutableListOf<Any?>()
        graph.traversal().V()
            .sideEffect { v -> log.add(v.id()) }
            .discard()
        log.size shouldBe graph.vertices.size
    }

    "property mutation applied before discard" {
        graph.traversal().V()
            .property("migrated", true)
            .discard()
        for (v in graph.vertices().asSequence()) {
            v.value<Boolean>("migrated") shouldBe true
        }
    }

    "discard and iterate produce equivalent side effects" {
        val logDiscard = mutableListOf<Any?>()
        val logIterate = mutableListOf<Any?>()

        graph.traversal().V()
            .sideEffect { v -> logDiscard.add(v.id()) }
            .discard()
        graph.traversal().V()
            .sideEffect { v -> logIterate.add(v.id()) }
            .iterate()

        logDiscard.map { it.toString() }.sorted() shouldBe logIterate.map { it.toString() }.sorted()
    }
})
