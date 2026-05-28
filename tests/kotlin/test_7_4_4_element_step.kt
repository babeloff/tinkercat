package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.4.4: element() Step.
 *
 * All tests call g.traversal().V().properties(...).element() to navigate from
 * a property back to its owning vertex or edge.
 * The properties() step is implemented; element() is also implemented (task 7.4.4).
 * Mirrors tests/python/test_7_4_4_element_step.py.
 */
class Test_7_4_4_ElementStep : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    "element step returns the owning vertex" {
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Alice")
        val owners = graph.traversal().V()
            .properties<String>("name")
            .element()
            .toList()
        owners shouldHaveSize 1
        owners[0].label() shouldBe "person"
    }

    "element step returns the owning edge" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        a.addEdge("knows", b, "weight", 1.0)
        val owners = graph.traversal().E()
            .properties<Double>("weight")
            .element()
            .toList()
        owners shouldHaveSize 1
        owners[0].label() shouldBe "knows"
    }

    "element step dedup collapses multi-property hits to one vertex" {
        graph.addVertex(TinkerVertex.T.label, "person", "phone1", "111", "phone2", "222")
        val owners = graph.traversal().V()
            .properties<String>("phone1", "phone2")
            .element()
            .dedup()
            .toList()
        owners shouldHaveSize 1
    }

    "element step on empty property traversal returns empty list" {
        val result = graph.traversal().V()
            .properties<String>("nonexistent")
            .element()
            .toList()
        result shouldBe emptyList()
    }

    "element step round-trip: property value matches owning vertex property" {
        graph.addVertex(TinkerVertex.T.label, "person", "name", "Bob")
        val owners = graph.traversal().V()
            .properties<String>("name")
            .element()
            .toList()
        owners[0].value<String>("name") shouldBe "Bob"
    }

    "element step works for vertex and edge properties in same graph" {
        val n1 = graph.addVertex(TinkerVertex.T.label, "node", "x", 1)
        val n2 = graph.addVertex(TinkerVertex.T.label, "n")
        val n3 = graph.addVertex(TinkerVertex.T.label, "n")
        n2.addEdge("link", n3, "y", 2)

        val vertexOwners = graph.traversal().V().hasLabel("node")
            .properties<Int>("x").element().toList()
        val edgeOwners = graph.traversal().E()
            .properties<Int>("y").element().toList()

        vertexOwners[0].label() shouldBe "node"
        edgeOwners[0].label() shouldBe "link"
    }

    "element step result has the expected label" {
        graph.addVertex(TinkerVertex.T.label, "software", "name", "lop")
        val owners = graph.traversal().V()
            .properties<String>("name")
            .element()
            .toList()
        owners[0].label() shouldBe "software"
    }
})
