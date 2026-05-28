package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.collections.shouldContain
import io.kotest.matchers.collections.shouldHaveSize
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import org.apache.tinkerpop.gremlin.tinkercat.algorithms.breadthFirstSearch
import org.apache.tinkerpop.gremlin.tinkercat.algorithms.depthFirstSearch
import org.apache.tinkerpop.gremlin.tinkercat.algorithms.hasCycle
import org.apache.tinkerpop.gremlin.tinkercat.algorithms.isConnected
import org.apache.tinkerpop.gremlin.tinkercat.algorithms.shortestPath
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 2.1.2: Graph Algorithms.
 *
 * Validates BFS, DFS, shortest path, connectivity, and cycle detection
 * implemented as extension functions on TinkerCat.
 * Mirrors tests/python/test_2_1_2_graph_algorithms.py.
 */
class Test_2_1_2_GraphAlgorithms : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest { graph = TinkerCat.open() }

    "bfs on single vertex returns just that vertex" {
        val v = graph.addVertex(TinkerVertex.T.label, "node")
        val result = graph.breadthFirstSearch(v).toList()
        result shouldHaveSize 1
        result[0].id() shouldBe v.id()
    }

    "bfs visits all vertices in a linear chain" {
        val v1 = graph.addVertex(TinkerVertex.T.label, "node")
        val v2 = graph.addVertex(TinkerVertex.T.label, "node")
        val v3 = graph.addVertex(TinkerVertex.T.label, "node")
        v1.addEdge("next", v2)
        v2.addEdge("next", v3)
        val result = graph.breadthFirstSearch(v1).toList()
        result shouldHaveSize 3
    }

    "bfs visits closer vertices before farther ones" {
        val root = graph.addVertex(TinkerVertex.T.label, "node")
        val child1 = graph.addVertex(TinkerVertex.T.label, "node")
        val child2 = graph.addVertex(TinkerVertex.T.label, "node")
        val grandchild = graph.addVertex(TinkerVertex.T.label, "node")
        root.addEdge("link", child1)
        root.addEdge("link", child2)
        child1.addEdge("link", grandchild)
        val result = graph.breadthFirstSearch(root).toList()
        val rootIdx = result.indexOfFirst { it.id() == root.id() }
        val grandIdx = result.indexOfFirst { it.id() == grandchild.id() }
        rootIdx shouldBe 0
        (grandIdx > 2) shouldBe true
    }

    "dfs on single vertex returns just that vertex" {
        val v = graph.addVertex(TinkerVertex.T.label, "node")
        val result = graph.depthFirstSearch(v).toList()
        result shouldHaveSize 1
    }

    "dfs visits all vertices in a chain" {
        val v1 = graph.addVertex(TinkerVertex.T.label, "node")
        val v2 = graph.addVertex(TinkerVertex.T.label, "node")
        val v3 = graph.addVertex(TinkerVertex.T.label, "node")
        v1.addEdge("next", v2)
        v2.addEdge("next", v3)
        val result = graph.depthFirstSearch(v1).toList()
        result shouldHaveSize 3
    }

    "bfs and dfs visit same set of vertices" {
        val v1 = graph.addVertex(TinkerVertex.T.label, "n")
        val v2 = graph.addVertex(TinkerVertex.T.label, "n")
        val v3 = graph.addVertex(TinkerVertex.T.label, "n")
        v1.addEdge("e", v2)
        v2.addEdge("e", v3)
        val bfsIds = graph.breadthFirstSearch(v1).map { it.id() }.toSet()
        val dfsIds = graph.depthFirstSearch(v1).map { it.id() }.toSet()
        bfsIds shouldBe dfsIds
    }

    "shortest path between adjacent vertices has length 2" {
        val a = graph.addVertex(TinkerVertex.T.label, "node")
        val b = graph.addVertex(TinkerVertex.T.label, "node")
        a.addEdge("link", b)
        val path = graph.shortestPath(a, b)
        path shouldNotBe null
        path!! shouldHaveSize 2
    }

    "shortest path returns null for disconnected vertices" {
        val a = graph.addVertex(TinkerVertex.T.label, "node")
        val b = graph.addVertex(TinkerVertex.T.label, "node")
        graph.shortestPath(a, b) shouldBe null
    }

    "shortest path from vertex to itself is single-element list" {
        val a = graph.addVertex(TinkerVertex.T.label, "node")
        val path = graph.shortestPath(a, a)
        path shouldNotBe null
        path!! shouldHaveSize 1
    }

    "connected graph is detected as connected" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        val c = graph.addVertex(TinkerVertex.T.label, "n")
        a.addEdge("e", b)
        b.addEdge("e", c)
        graph.isConnected() shouldBe true
    }

    "disconnected graph is detected as disconnected" {
        graph.addVertex(TinkerVertex.T.label, "n")
        graph.addVertex(TinkerVertex.T.label, "n")
        graph.isConnected() shouldBe false
    }

    "acyclic graph has no cycle" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        val c = graph.addVertex(TinkerVertex.T.label, "n")
        a.addEdge("e", b)
        b.addEdge("e", c)
        graph.hasCycle() shouldBe false
    }

    "graph with cycle is detected" {
        val a = graph.addVertex(TinkerVertex.T.label, "n")
        val b = graph.addVertex(TinkerVertex.T.label, "n")
        val c = graph.addVertex(TinkerVertex.T.label, "n")
        a.addEdge("e", b)
        b.addEdge("e", c)
        c.addEdge("e", a)
        graph.hasCycle() shouldBe true
    }
})
