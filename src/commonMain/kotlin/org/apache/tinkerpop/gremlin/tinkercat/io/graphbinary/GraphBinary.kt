package org.apache.tinkerpop.gremlin.tinkercat.io.graphbinary

import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat

/**
 * Stub API for GraphBinary 4.0 serialisation (task 7.6.1).
 *
 * Every function throws [UnsupportedOperationException] until the codec is implemented.
 * The signatures here define the contract that the implementation must satisfy.
 */

/** Serialises [graph] to the GraphBinary 4.0 wire format. Not yet implemented. */
fun writeGraph(graph: TinkerCat): ByteArray {
    throw UnsupportedOperationException("GraphBinary writeGraph() not yet implemented (task 7.6.1)")
}

/** Deserialises a [TinkerCat] graph from GraphBinary 4.0 bytes. Not yet implemented. */
fun readGraph(data: ByteArray): TinkerCat {
    throw UnsupportedOperationException("GraphBinary readGraph() not yet implemented (task 7.6.1)")
}

/**
 * Serialises a single scalar [value] (Int, Long, Float, Double, Boolean, String) to
 * GraphBinary bytes. Throws [IllegalArgumentException] for unsupported types.
 * Serialisation itself is not yet implemented (task 7.6.1).
 */
fun writeValue(value: Any?): ByteArray = when (value) {
    is Int, is Long, is Float, is Double, is Boolean, is String ->
        throw UnsupportedOperationException("GraphBinary writeValue() not yet implemented (task 7.6.1)")
    else ->
        throw IllegalArgumentException(
            "Unsupported type for GraphBinary serialization: ${value?.let { it::class.simpleName } ?: "null"}"
        )
}

/** Deserialises a single scalar value from GraphBinary bytes. Not yet implemented. */
fun readValue(data: ByteArray): Any? {
    throw UnsupportedOperationException("GraphBinary readValue() not yet implemented (task 7.6.1)")
}
