package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.structure.Direction
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.7.1: Lambda Deprecation for GLV Compatibility.
 *
 * Validates that anonymous traversal steps (hasLabel, has, hasNot, values) produce
 * the same results as the deprecated lambda forms they replace.  All tests use
 * the real TinkerCat traversal API — these tests ARE expected to pass.
 * Mirrors tests/python/test_7_7_1_lambda_deprecation.py.
 */
class Test_7_7_1_LambdaDeprecation : StringSpec({

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

    "hasLabel replaces filter-lambda: 4 persons in modern graph" {
        val result = graph.traversal().V().hasLabel("person").toList()
        result shouldHaveSize 4
    }

    "values replaces map-lambda: projects name property" {
        val names = graph.traversal().V()
            .hasLabel("person")
            .values<String>("name")
            .toList()
            .sorted()
        names shouldBe listOf("josh", "marko", "peter", "vadas")
    }

    "id projection replaces side-effect lambda: 6 ids in modern graph" {
        val ids = graph.traversal().V().id().toList()
        ids shouldHaveSize 6
    }

    "anonymous traversal filter is equivalent to hasLabel" {
        val viaHasLabel = graph.traversal().V().hasLabel("person").toList()
        val viaFilter   = graph.vertices().asSequence()
            .filter { it.label() == "person" }.toList()
        viaHasLabel.size shouldBe viaFilter.size
    }

    "values returns the correct projected names" {
        val names = graph.traversal().V()
            .hasLabel("person")
            .values<String>("name")
            .toList()
            .sorted()
        names shouldBe listOf("josh", "marko", "peter", "vadas")
    }

    "has is logically equivalent to filter with property check" {
        val viaHas    = graph.traversal().V().has("name", "marko").toList()
        val viaFilter = graph.vertices().asSequence()
            .filter { it.value<String>("name") == "marko" }.toList()
        viaHas shouldHaveSize 1
        viaHas.size shouldBe viaFilter.size
        viaHas[0].value<String>("name") shouldBe "marko"
    }

    "traversal does not alter the graph" {
        val before = graph.vertices.size
        graph.traversal().V().toList()
        graph.vertices.size shouldBe before
    }

    "hasNot replaces filter-lambda negation: 4 vertices have no lang property" {
        val result = graph.traversal().V().hasNot("lang").toList()
        result shouldHaveSize 4
    }
})
