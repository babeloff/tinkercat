package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.structure.Direction
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.1.1: Traversal Engine.
 *
 * Validates graph filtering and navigation via Kotlin sequence operations —
 * the native equivalent of the Python GraphTraversal steps has(), has_label(),
 * values(), out(), in_(), and count().
 * Mirrors tests/python/test_7_1_1_traversal_engine.py.
 */
class Test_7_1_1_TraversalEngine : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest {
        graph = TinkerCat.open()
        // Build the "modern" TinkerPop toy graph
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

    "all vertices are reachable" {
        graph.vertices().asSequence().toList() shouldHaveSize 6
    }

    "all edges are reachable" {
        graph.edges().asSequence().toList() shouldHaveSize 6
    }

    "has_label equivalent filters by label" {
        val persons = graph.vertices().asSequence()
            .filter { it.label() == "person" }.toList()
        persons shouldHaveSize 4
    }

    "has equivalent filters by property equality" {
        val markoList = graph.vertices().asSequence()
            .filter { it.value<String>("name") == "marko" }.toList()
        markoList shouldHaveSize 1
        markoList[0].value<String>("name") shouldBe "marko"
    }

    "has_not equivalent filters vertices without a property" {
        val noLang = graph.vertices().asSequence()
            .filter { it.value<String>("lang") == null }.toList()
        noLang shouldHaveSize 4  // 4 persons have no lang property
    }

    "values equivalent projects a property across vertices" {
        val names = graph.vertices().asSequence()
            .filter { it.label() == "person" }
            .mapNotNull { it.value<String>("name") }
            .sorted().toList()
        names shouldBe listOf("josh", "marko", "peter", "vadas")
    }

    "out equivalent navigates from vertex to its out-neighbours" {
        val marko = graph.vertices().asSequence()
            .first { it.value<String>("name") == "marko" }
        val outNeighbours = marko.edges(Direction.OUT).asSequence()
            .map { it.inVertex() }.toList()
        outNeighbours shouldHaveSize 3
    }

    "in equivalent navigates to in-neighbours" {
        val lop = graph.vertices().asSequence()
            .first { it.value<String>("name") == "lop" }
        val creators = lop.edges(Direction.IN).asSequence()
            .map { it.outVertex() }.toList()
        creators shouldHaveSize 3
    }

    "count equivalent uses vertices.size" {
        graph.vertices.size shouldBe 6
        graph.edges.size shouldBe 6
    }

    "chained filter by label then property" {
        val result = graph.vertices().asSequence()
            .filter { it.label() == "person" }
            .filter { it.value<String>("name") == "josh" }
            .toList()
        result shouldHaveSize 1
    }

    "edge label filter on out-edges" {
        val marko = graph.vertices().asSequence()
            .first { it.value<String>("name") == "marko" }
        val knows = marko.edges(Direction.OUT, "knows").asSequence().toList()
        knows shouldHaveSize 2
    }

    "two-hop traversal: person -> created -> software" {
        val marko = graph.vertices().asSequence()
            .first { it.value<String>("name") == "marko" }
        val created = marko.edges(Direction.OUT, "created").asSequence()
            .map { it.inVertex() }
            .filter { it.label() == "software" }
            .toList()
        created shouldHaveSize 1
        created[0].value<String>("name") shouldBe "lop"
    }
})
