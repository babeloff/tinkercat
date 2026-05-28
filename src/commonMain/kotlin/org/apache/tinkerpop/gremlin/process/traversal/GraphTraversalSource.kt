package org.apache.tinkerpop.gremlin.process.traversal

import org.apache.tinkerpop.gremlin.structure.Graph
import org.apache.tinkerpop.gremlin.structure.Vertex
import org.apache.tinkerpop.gremlin.structure.Edge

/**
 * The starting point for graph traversals.
 *
 * Obtained via [Graph.traversal] (or [TinkerCat.traversal] on a TinkerCat instance).
 * Every traversal begins here with [V] or [E].
 *
 * ```kotlin
 * val g = graph.traversal()
 * val names = g.V().hasLabel("person").values<String>("name").toList()
 * ```
 */
class GraphTraversalSource(val graph: Graph) {

    // ── Vertex starters ───────────────────────────────────────────────────────

    /**
     * Start a traversal from all vertices (no arguments) or from specific vertices
     * identified by [vertexIds].
     */
    fun V(vararg vertexIds: Any?): GraphTraversal<Vertex, Vertex> =
        GraphTraversal(graph.vertices(*vertexIds).asSequence())

    // ── Edge starters ─────────────────────────────────────────────────────────

    /**
     * Start a traversal from all edges (no arguments) or from specific edges
     * identified by [edgeIds].
     */
    fun E(vararg edgeIds: Any?): GraphTraversal<Edge, Edge> =
        GraphTraversal(graph.edges(*edgeIds).asSequence())

    // ── Mutation starters ─────────────────────────────────────────────────────

    /**
     * Add a vertex with [label] to the graph and start a traversal from it.
     */
    fun addV(label: String = Vertex.DEFAULT_LABEL): GraphTraversal<Vertex, Vertex> {
        val v = graph.addVertex(label)
        return GraphTraversal(sequenceOf(v))
    }

    /**
     * Add a vertex with the given properties and start a traversal from it.
     */
    fun addV(label: String, vararg keyValues: Any?): GraphTraversal<Vertex, Vertex> {
        val args: Array<Any?> = (listOf<Any?>("label", label) + keyValues.toList()).toTypedArray()
        val v = graph.addVertex(*args)
        return GraphTraversal(sequenceOf(v))
    }
}
