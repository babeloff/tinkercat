@file:JsExport

package org.apache.tinkerpop.gremlin.tinkercat.js

import kotlin.js.JsExport
import kotlin.js.JsName
import org.apache.tinkerpop.gremlin.structure.*
import org.apache.tinkerpop.gremlin.tinkercat.structure.*
import org.apache.tinkerpop.gremlin.tinkercat.algorithms.*

/**
 * JavaScript/TypeScript facade for TinkerCat library.
 *
 * This facade provides a JavaScript-friendly API with proper TypeScript definitions.
 * All functions are exported as top-level functions to comply with Kotlin/JS @JsExport
 * restrictions while providing an intuitive API for JavaScript developers.
 *
 * @since 1.0.0
 */

// Graph Creation and Management

/**
 * Create a new TinkerCat instance with default configuration.
 *
 * @return New TinkerCat instance
 */
@JsExport
fun createTinkerCat(): TinkerCat {
    return TinkerCat.open()
}

/**
 * Create a new TinkerCat instance with custom configuration.
 *
 * @param config Configuration object with graph settings
 * @return New TinkerCat instance
 */
@JsExport
@JsName("createTinkerCatWithConfig")
fun createTinkerCat(config: Map<String, Any?>): TinkerCat {
    return TinkerCat.open(config)
}

/**
 * Create a TinkerCat with common configuration presets.
 *
 * @param allowNullProperties Whether to allow null property values
 * @param defaultCardinality Default vertex property cardinality ("SINGLE", "LIST", or "SET")
 * @return New TinkerCat instance
 */
@JsExport
fun createTinkerCatWithSettings(
    allowNullProperties: Boolean = false,
    defaultCardinality: String = "SINGLE"
): TinkerCat {
    val config = mapOf(
        TinkerCat.GREMLIN_TINKERCAT_ALLOW_NULL_PROPERTY_VALUES to allowNullProperties,
        TinkerCat.GREMLIN_TINKERCAT_DEFAULT_VERTEX_PROPERTY_CARDINALITY to defaultCardinality
    )
    return TinkerCat.open(config)
}

// Vertex Operations

/**
 * Add a vertex to the graph with properties.
 *
 * @param graph The graph to add the vertex to
 * @param properties Properties as key-value pairs
 * @return The created vertex
 */
@JsExport
fun addVertex(graph: TinkerCat, properties: Map<String, Any?>): Vertex {
    return graph.addVertex(properties)
}

/**
 * Add a vertex with a single property.
 *
 * @param graph The graph to add the vertex to
 * @param key Property key
 * @param value Property value
 * @return The created vertex
 */
@JsExport
@JsName("addVertexWithProperty")
fun addVertex(graph: TinkerCat, key: String, value: Any?): Vertex {
    return graph.addVertex(mapOf(key to value))
}

/**
 * Add a vertex with label and properties.
 *
 * @param graph The graph to add the vertex to
 * @param label Vertex label
 * @param properties Properties as key-value pairs
 * @return The created vertex
 */
@JsExport
fun addVertexWithLabel(graph: TinkerCat, label: String, properties: Map<String, Any?>): Vertex {
    val props = properties.toMutableMap()
    props["label"] = label
    return graph.addVertex(props)
}

/**
 * Add a vertex with label and properties supplied as parallel arrays.
 * This variant is safe to call from JavaScript (avoids Map iteration issues).
 *
 * @param graph The graph to add the vertex to
 * @param label Vertex label
 * @param keys Property keys
 * @param values Property values (same length as keys)
 * @return The created vertex
 */
@JsExport
fun addVertexWithLabelAndArrays(graph: TinkerCat, label: String, keys: Array<String>, values: Array<Any?>): Vertex {
    val props = mutableMapOf<String, Any?>("label" to label)
    keys.forEachIndexed { i, key -> props[key] = values[i] }
    return graph.addVertex(props)
}

/**
 * Add a vertex with properties supplied as parallel arrays (no label).
 * This variant is safe to call from JavaScript (avoids Map iteration issues).
 *
 * @param graph The graph to add the vertex to
 * @param keys Property keys
 * @param values Property values (same length as keys)
 * @return The created vertex
 */
@JsExport
fun addVertexWithArrays(graph: TinkerCat, keys: Array<String>, values: Array<Any?>): Vertex {
    val props = mutableMapOf<String, Any?>()
    keys.forEachIndexed { i, key -> props[key] = values[i] }
    return graph.addVertex(props)
}

/**
 * Get the label of a graph element (vertex or edge).
 * Provides JavaScript-accessible access to the mangled label() method.
 *
 * @param element The element to get the label from
 * @return The element's label string
 */
@JsExport
fun getLabel(element: Element): String = element.label()

/**
 * Get the ID of a graph element.
 * Provides JavaScript-accessible access to the mangled id() method.
 *
 * @param element The element to get the ID from
 * @return The element's ID
 */
@JsExport
fun getElementId(element: Element): Any? = element.id()

/**
 * Remove a graph element (vertex or edge) from the graph.
 * Provides JavaScript-accessible access to the mangled remove() method.
 *
 * @param element The element to remove
 */
@JsExport
fun removeElement(element: Element) = element.remove()

/**
 * Get the in-vertex (target) of an edge.
 * Provides JavaScript-accessible access to the mangled inVertex() method.
 *
 * @param edge The edge to get the in-vertex from
 * @return The in-vertex
 */
@JsExport
fun getInVertex(edge: Edge): Vertex = edge.inVertex()

/**
 * Get the out-vertex (source) of an edge.
 * Provides JavaScript-accessible access to the mangled outVertex() method.
 *
 * @param edge The edge to get the out-vertex from
 * @return The out-vertex
 */
@JsExport
fun getOutVertex(edge: Edge): Vertex = edge.outVertex()

/**
 * Get a vertex by ID.
 *
 * @param graph The graph to search in
 * @param id The vertex ID
 * @return The vertex or null if not found
 */
@JsExport
fun getVertex(graph: TinkerCat, id: Any?): Vertex? {
    return graph.vertex(id)
}

/**
 * Get all vertices in the graph as an array.
 *
 * @param graph The graph to get vertices from
 * @return Array of all vertices
 */
@JsExport
fun getAllVertices(graph: TinkerCat): Array<Vertex> {
    return graph.vertices().asSequence().toList().toTypedArray()
}

/**
 * Get specific vertices by IDs as an array.
 *
 * @param graph The graph to get vertices from
 * @param ids Array of vertex IDs
 * @return Array of matching vertices
 */
@JsExport
fun getVerticesByIds(graph: TinkerCat, ids: Array<Any?>): Array<Vertex> {
    return graph.vertices(*ids).asSequence().toList().toTypedArray()
}

// Edge Operations

/**
 * Add an edge between two vertices.
 *
 * @param outVertex Source vertex
 * @param label Edge label
 * @param inVertex Target vertex
 * @param properties Edge properties
 * @return The created edge
 */
@JsExport
fun addEdge(outVertex: Vertex, label: String, inVertex: Vertex, properties: Map<String, Any?>): Edge {
    return outVertex.addEdge(label, inVertex, properties)
}

/**
 * Add an edge with a single property.
 *
 * @param outVertex Source vertex
 * @param label Edge label
 * @param inVertex Target vertex
 * @param propertyKey Property key
 * @param propertyValue Property value
 * @return The created edge
 */
@JsExport
@JsName("addEdgeWithProperty")
fun addEdge(outVertex: Vertex, label: String, inVertex: Vertex, propertyKey: String, propertyValue: Any?): Edge {
    return outVertex.addEdge(label, inVertex, mapOf(propertyKey to propertyValue))
}

/**
 * Add an edge with properties supplied as parallel arrays.
 * This variant is safe to call from JavaScript (avoids Map iteration issues).
 *
 * @param outVertex Source vertex
 * @param label Edge label
 * @param inVertex Target vertex
 * @param keys Property keys
 * @param values Property values (same length as keys)
 * @return The created edge
 */
@JsExport
fun addEdgeWithArrays(outVertex: Vertex, label: String, inVertex: Vertex, keys: Array<String>, values: Array<Any?>): Edge {
    val props = mutableMapOf<String, Any?>()
    keys.forEachIndexed { i, key -> props[key] = values[i] }
    return outVertex.addEdge(label, inVertex, props)
}

/**
 * Get an edge by ID.
 *
 * @param graph The graph to search in
 * @param id The edge ID
 * @return The edge or null if not found
 */
@JsExport
fun getEdge(graph: TinkerCat, id: Any?): Edge? {
    return graph.edge(id)
}

/**
 * Get all edges in the graph as an array.
 *
 * @param graph The graph to get edges from
 * @return Array of all edges
 */
@JsExport
fun getAllEdges(graph: TinkerCat): Array<Edge> {
    return graph.edges().asSequence().toList().toTypedArray()
}

/**
 * Get edges from a vertex in a specific direction as an array.
 *
 * @param vertex The vertex to get edges from
 * @param direction Direction ("OUT", "IN", or "BOTH")
 * @param labels Optional edge labels to filter by
 * @return Array of edges
 */
@JsExport
fun getVertexEdges(vertex: Vertex, direction: String, labels: Array<String> = emptyArray()): Array<Edge> {
    val dir = when (direction.uppercase()) {
        "OUT" -> Direction.OUT
        "IN" -> Direction.IN
        "BOTH" -> Direction.BOTH
        else -> throw IllegalArgumentException("Invalid direction: $direction. Use 'OUT', 'IN', or 'BOTH'")
    }
    return vertex.edges(dir, *labels).asSequence().toList().toTypedArray()
}

/**
 * Get vertices connected to a vertex as an array.
 *
 * @param vertex The vertex to get connected vertices from
 * @param direction Direction ("OUT", "IN", or "BOTH")
 * @param labels Optional edge labels to filter by
 * @return Array of connected vertices
 */
@JsExport
fun getConnectedVertices(vertex: Vertex, direction: String, labels: Array<String> = emptyArray()): Array<Vertex> {
    val dir = when (direction.uppercase()) {
        "OUT" -> Direction.OUT
        "IN" -> Direction.IN
        "BOTH" -> Direction.BOTH
        else -> throw IllegalArgumentException("Invalid direction: $direction. Use 'OUT', 'IN', or 'BOTH'")
    }
    return vertex.vertices(dir, *labels).asSequence().toList().toTypedArray()
}

// Property Operations

/**
 * Set a property on an element (vertex or edge).
 *
 * @param element The element to set the property on
 * @param key Property key
 * @param value Property value
 * @return The created property
 */
@JsExport
fun setProperty(element: Element, key: String, value: Any?): Property<Any?> {
    return element.property(key, value)
}

/**
 * Get a property value from an element.
 *
 * @param element The element to get the property from
 * @param key Property key
 * @return Property value or null if not found
 */
@JsExport
fun getPropertyValue(element: Element, key: String): Any? {
    return element.value<Any?>(key)
}

/**
 * Get all property keys from an element as an array.
 *
 * @param element The element to get keys from
 * @return Array of property keys
 */
@JsExport
fun getPropertyKeys(element: Element): Array<String> {
    return element.keys().toTypedArray()
}

/**
 * Check if an element has a property with the given key.
 *
 * @param element The element to check
 * @param key Property key
 * @return true if property exists, false otherwise
 */
@JsExport
fun hasProperty(element: Element, key: String): Boolean {
    return element.keys().contains(key)
}

// Index Operations

/**
 * Create an index on a property for faster lookups.
 *
 * @param graph The graph to create the index on
 * @param propertyKey The property key to index
 * @param elementType Element type ("Vertex" or "Edge")
 */
@JsExport
fun createIndex(graph: TinkerCat, propertyKey: String, elementType: String) {
    val elementClass = when (elementType.lowercase()) {
        "vertex" -> Vertex::class
        "edge" -> Edge::class
        else -> throw IllegalArgumentException("Invalid element type: $elementType. Use 'Vertex' or 'Edge'")
    }
    graph.createIndex(propertyKey, elementClass)
}

/**
 * Create a composite index on multiple properties.
 *
 * @param graph The graph to create the index on
 * @param propertyKeys Array of property keys to index together
 * @param elementType Element type ("Vertex" or "Edge")
 */
@JsExport
fun createCompositeIndex(graph: TinkerCat, propertyKeys: Array<String>, elementType: String) {
    val elementClass = when (elementType.lowercase()) {
        "vertex" -> Vertex::class
        "edge" -> Edge::class
        else -> throw IllegalArgumentException("Invalid element type: $elementType. Use 'Vertex' or 'Edge'")
    }
    graph.createCompositeIndex(propertyKeys.toList(), elementClass)
}

/**
 * Create a range index for efficient range queries.
 *
 * @param graph The graph to create the index on
 * @param propertyKey The property key to index (must contain comparable values)
 * @param elementType Element type ("Vertex" or "Edge")
 */
@JsExport
fun createRangeIndex(graph: TinkerCat, propertyKey: String, elementType: String) {
    val elementClass = when (elementType.lowercase()) {
        "vertex" -> Vertex::class
        "edge" -> Edge::class
        else -> throw IllegalArgumentException("Invalid element type: $elementType. Use 'Vertex' or 'Edge'")
    }
    graph.createRangeIndex(propertyKey, elementClass)
}

// Graph Algorithms

/**
 * Perform breadth-first search from a starting vertex.
 *
 * @param graph The graph to search in
 * @param startVertex The starting vertex
 * @return Array of vertices in BFS order
 */
@JsExport
fun breadthFirstSearch(graph: TinkerCat, startVertex: Vertex): Array<Vertex> {
    return graph.breadthFirstSearch(startVertex)
        .toList().toTypedArray()
}

/**
 * Perform depth-first search from a starting vertex.
 *
 * @param graph The graph to search in
 * @param startVertex The starting vertex
 * @return Array of vertices in DFS order
 */
@JsExport
fun depthFirstSearch(graph: TinkerCat, startVertex: Vertex): Array<Vertex> {
    return graph.depthFirstSearch(startVertex)
        .toList().toTypedArray()
}

/**
 * Find the shortest path between two vertices.
 *
 * @param graph The graph to search in
 * @param fromVertex Starting vertex
 * @param toVertex Target vertex
 * @return Array representing the shortest path, or null if no path exists
 */
@JsExport
fun shortestPath(graph: TinkerCat, fromVertex: Vertex, toVertex: Vertex): Array<Vertex>? {
    return graph.shortestPath(fromVertex, toVertex)
        ?.toList()?.toTypedArray()
}

/**
 * Find all connected components in the graph.
 *
 * @param graph The graph to analyze
 * @return Array of arrays, where each inner array represents vertices in one connected component
 */
@JsExport
fun findConnectedComponents(graph: TinkerCat): Array<Array<Vertex>> {
    return graph.connectedComponents()
        .map { it.toList().toTypedArray() }.toTypedArray()
}

/**
 * Check if the graph contains any cycles.
 *
 * @param graph The graph to check
 * @return true if the graph has at least one cycle, false otherwise
 */
@JsExport
fun hasCycle(graph: TinkerCat): Boolean {
    return graph.hasCycle()
}

// Utility Operations

/**
 * Get the total number of vertices in the graph.
 *
 * @param graph The graph to count vertices in
 * @return Number of vertices
 */
@JsExport
fun getVertexCount(graph: TinkerCat): Int {
    return graph.vertices().asSequence().count()
}

/**
 * Get the total number of edges in the graph.
 *
 * @param graph The graph to count edges in
 * @return Number of edges
 */
@JsExport
fun getEdgeCount(graph: TinkerCat): Int {
    return graph.edges().asSequence().count()
}

/**
 * Clear all vertices and edges from the graph.
 *
 * @param graph The graph to clear
 */
@JsExport
fun clearGraph(graph: TinkerCat) {
    // Remove all vertices (edges will be automatically removed)
    val vertices = graph.vertices().asSequence().toList()
    vertices.forEach { it.remove() }
}

/**
 * Get basic graph statistics.
 *
 * @param graph The graph to analyze
 * @return Object containing vertex count, edge count, and other basic metrics
 */
@JsExport
fun getGraphStatistics(graph: TinkerCat): Map<String, Any> {
    val vertexCount = getVertexCount(graph)
    val edgeCount = getEdgeCount(graph)

    return mapOf(
        "vertexCount" to vertexCount,
        "edgeCount" to edgeCount,
        "avgDegree" to if (vertexCount > 0) (2.0 * edgeCount) / vertexCount else 0.0,
        "density" to if (vertexCount > 1) (2.0 * edgeCount) / (vertexCount * (vertexCount - 1)) else 0.0
    )
}
