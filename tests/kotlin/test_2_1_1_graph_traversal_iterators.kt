package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import org.apache.tinkerpop.gremlin.structure.Direction
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 2.1.1: Graph Traversal Iterators.
 *
 * Validates vertex and edge iteration, label filtering, and property-based
 * filtering using Kotlin sequences over TinkerCat's native iterators.
 * Mirrors tests/python/test_2_1_1_graph_traversal_iterators.py.
 */
class Test_2_1_1_GraphTraversalIterators : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    "empty graph has no vertices" {
        graph.vertices().asSequence().toList() shouldHaveSize 0
    }

    "empty graph has no edges" {
        graph.edges().asSequence().toList() shouldHaveSize 0
    }

    "added vertex appears in vertex iterator" {
        val v = graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        val all = graph.vertices().asSequence().toList()
        all shouldHaveSize 1
        all[0].id() shouldBe v.id()
    }

    "vertex count matches actual vertices" {
        repeat(5) { graph.addVertex(TinkerVertex.T.label, "node") }
        graph.vertices.size shouldBe 5
    }

    "edge count matches actual edges" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        val c = graph.addVertex(TinkerVertex.T.label, "n")
        a.addEdge("link", b)
        a.addEdge("link", c)
        graph.edges.size shouldBe 2
    }

    "vertex label is preserved after creation" {
        val v = graph.addVertex(TinkerVertex.T.label, "person", "name", "Bob")
        v.label() shouldBe "person"
    }

    "vertex property is retrievable via value()" {
        val v = graph.addVertex(TinkerVertex.T.label, "person", "name", "Carol", "age", 30)
        v.value<String>("name") shouldBe "Carol"
        v.value<Int>("age") shouldBe 30
    }

    "filter vertices by label using sequence" {
        repeat(3) { graph.addVertex(TinkerVertex.T.label, "person") }
        repeat(2) { graph.addVertex(TinkerVertex.T.label, "software") }
        val persons = graph.vertices().asSequence().filter { it.label() == "person" }.toList()
        persons shouldHaveSize 3
    }

    "filter vertices by property value using sequence" {
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice", "age", 25)
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Bob", "age", 30)
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Carol", "age", 35)
        val adults = graph.vertices().asSequence()
            .filter { it.value<Int>("age") != null && it.value<Int>("age")!! >= 30 }
            .toList()
        adults shouldHaveSize 2
    }

    "edge connects correct out and in vertices" {
        val a = graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        val b = graph.addVertex(TinkerVertex.T.label, "person", "name", "Bob")
        a.addEdge("knows", b)
        val edge = graph.edges().asSequence().first()
        edge.outVertex().id() shouldBe a.id()
        edge.inVertex().id() shouldBe b.id()
    }

    "edge label is preserved" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        a.addEdge("knows", b)
        graph.edges().asSequence().first().label() shouldBe "knows"
    }

    "vertex out-edges are navigable" {
        val a = graph.addVertex(TinkerVertex.T.label, "person")
        val b = graph.addVertex(TinkerVertex.T.label, "person")
        val c = graph.addVertex(TinkerVertex.T.label, "person")
        a.addEdge("knows", b)
        a.addEdge("knows", c)
        val outEdges = a.edges(Direction.OUT).asSequence().toList()
        outEdges shouldHaveSize 2
    }

    "vertex in-edges are navigable" {
        val a = graph.addVertex(TinkerVertex.T.label, "person")
        val b = graph.addVertex(TinkerVertex.T.label, "person")
        b.addEdge("knows", a)
        val inEdges = a.edges(Direction.IN).asSequence().toList()
        inEdges shouldHaveSize 1
    }

    "missing property returns null" {
        val v = graph.addVertex(TinkerVertex.T.label, "node")
        v.value<String>("nonexistent") shouldBe null
    }

    "vertex id is non-null" {
        val v = graph.addVertex(TinkerVertex.T.label, "node")
        v.id() shouldNotBe null
    }

    "multiple vertices have distinct ids" {
        val v1 = graph.addVertex(TinkerVertex.T.label, "node")
        val v2 = graph.addVertex(TinkerVertex.T.label, "node")
        v1.id() shouldNotBe v2.id()
    }
})
