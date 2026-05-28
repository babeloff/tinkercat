package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.tinkercat.io.graphbinary.readGraph
import org.apache.tinkerpop.gremlin.tinkercat.io.graphbinary.readValue
import org.apache.tinkerpop.gremlin.tinkercat.io.graphbinary.writeGraph
import org.apache.tinkerpop.gremlin.tinkercat.io.graphbinary.writeValue
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.6.1: GraphBinary 4.0 Serialisation.
 *
 * All tests call writeGraph / readGraph / writeValue / readValue from the
 * graphbinary package.  Every function throws UnsupportedOperationException
 * until the codec is implemented.
 * Mirrors tests/python/test_7_6_1_graphbinary.py.
 */
class Test_7_6_1_GraphBinary : StringSpec({

    fun buildModernGraph(graph: TinkerCat) {
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

    "round-trip preserves vertex count" {
        val g1 = TinkerCat.open()
        buildModernGraph(g1)
        val data = writeGraph(g1)
        val g2 = readGraph(data)
        g2.vertices.size shouldBe g1.vertices.size
        g1.close(); g2.close()
    }

    "round-trip preserves edge count" {
        val g1 = TinkerCat.open()
        buildModernGraph(g1)
        val data = writeGraph(g1)
        val g2 = readGraph(data)
        g2.edges.size shouldBe g1.edges.size
        g1.close(); g2.close()
    }

    "round-trip preserves string property" {
        val g1 = TinkerCat.open()
        g1.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        val data = writeGraph(g1)
        val g2 = readGraph(data)
        val v = g2.vertices().asSequence().first()
        v.value<String>("name") shouldBe "Alice"
        g1.close(); g2.close()
    }

    "round-trip preserves int property" {
        val g1 = TinkerCat.open()
        g1.addVertex(TinkerVertex.T.label, "person", "age", 30)
        val data = writeGraph(g1)
        val g2 = readGraph(data)
        val v = g2.vertices().asSequence().first()
        v.value<Int>("age") shouldBe 30
        g1.close(); g2.close()
    }

    "round-trip preserves float property" {
        val g1 = TinkerCat.open()
        g1.addVertex(TinkerVertex.T.label, "item", "score", 3.14)
        val data = writeGraph(g1)
        val g2 = readGraph(data)
        val v = g2.vertices().asSequence().first()
        val diff = (v.value<Double>("score")!! - 3.14)
        (diff < 1e-9 && diff > -1e-9) shouldBe true
        g1.close(); g2.close()
    }

    "round-trip preserves boolean property" {
        val g1 = TinkerCat.open()
        g1.addVertex(TinkerVertex.T.label, "item", "active", true)
        val data = writeGraph(g1)
        val g2 = readGraph(data)
        val v = g2.vertices().asSequence().first()
        v.value<Boolean>("active") shouldBe true
        g1.close(); g2.close()
    }

    "writeValue and readValue round-trip an int" {
        val data = writeValue(42)
        readValue(data) shouldBe 42
    }

    "writeValue and readValue round-trip a string" {
        val data = writeValue("hello")
        readValue(data) shouldBe "hello"
    }

    "writeValue and readValue round-trip boolean true" {
        val data = writeValue(true)
        readValue(data) shouldBe true
    }

    "writeValue and readValue round-trip boolean false" {
        val data = writeValue(false)
        readValue(data) shouldBe false
    }

    "writeValue throws IllegalArgumentException for unsupported type" {
        val caught = runCatching { writeValue(listOf(1, 2, 3)) }.exceptionOrNull()
        (caught is IllegalArgumentException) shouldBe true
    }

    "empty graph round-trip produces empty graph" {
        val g1 = TinkerCat.open()
        val data = writeGraph(g1)
        val g2 = readGraph(data)
        g2.vertices.size shouldBe 0
        g2.edges.size shouldBe 0
        g1.close(); g2.close()
    }
})
