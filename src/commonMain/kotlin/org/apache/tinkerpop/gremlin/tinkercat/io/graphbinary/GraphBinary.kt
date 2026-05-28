package org.apache.tinkerpop.gremlin.tinkercat.io.graphbinary

import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

private const val TYPE_INT: Byte    = 0x01
private const val TYPE_LONG: Byte   = 0x02
private const val TYPE_FLOAT: Byte  = 0x03
private const val TYPE_DOUBLE: Byte = 0x04
private const val TYPE_BOOL: Byte   = 0x05
private const val TYPE_STRING: Byte = 0x06

// ── Write helpers ─────────────────────────────────────────────────────────────

private fun MutableList<Byte>.addInt(v: Int) {
    add((v ushr 24).toByte())
    add((v ushr 16).toByte())
    add((v ushr  8).toByte())
    add(v.toByte())
}

private fun MutableList<Byte>.addLong(v: Long) {
    add((v ushr 56).toByte())
    add((v ushr 48).toByte())
    add((v ushr 40).toByte())
    add((v ushr 32).toByte())
    add((v ushr 24).toByte())
    add((v ushr 16).toByte())
    add((v ushr  8).toByte())
    add(v.toByte())
}

private fun MutableList<Byte>.addString(s: String) {
    val bytes = s.encodeToByteArray()
    addInt(bytes.size)
    for (b in bytes) add(b)
}

private fun MutableList<Byte>.addTaggedValue(v: Any?) {
    when (v) {
        is Int     -> { add(TYPE_INT);    addInt(v) }
        is Long    -> { add(TYPE_LONG);   addLong(v) }
        is Float   -> { add(TYPE_FLOAT);  addInt(v.toBits()) }
        is Double  -> { add(TYPE_DOUBLE); addLong(v.toBits()) }
        is Boolean -> { add(TYPE_BOOL);   add(if (v) 1 else 0) }
        is String  -> { add(TYPE_STRING); addString(v) }
        else -> throw IllegalArgumentException(
            "Unsupported type for GraphBinary serialization: ${v?.let { it::class.simpleName } ?: "null"}"
        )
    }
}

// ── Read helpers ──────────────────────────────────────────────────────────────

private class Reader(private val data: ByteArray) {
    var pos: Int = 0

    fun int(): Int {
        val v = ((data[pos    ].toInt() and 0xFF) shl 24) or
                ((data[pos + 1].toInt() and 0xFF) shl 16) or
                ((data[pos + 2].toInt() and 0xFF) shl  8) or
                 (data[pos + 3].toInt() and 0xFF)
        pos += 4
        return v
    }

    fun long(): Long {
        val v = ((data[pos    ].toLong() and 0xFF) shl 56) or
                ((data[pos + 1].toLong() and 0xFF) shl 48) or
                ((data[pos + 2].toLong() and 0xFF) shl 40) or
                ((data[pos + 3].toLong() and 0xFF) shl 32) or
                ((data[pos + 4].toLong() and 0xFF) shl 24) or
                ((data[pos + 5].toLong() and 0xFF) shl 16) or
                ((data[pos + 6].toLong() and 0xFF) shl  8) or
                 (data[pos + 7].toLong() and 0xFF)
        pos += 8
        return v
    }

    fun string(): String {
        val len = int()
        val bytes = data.copyOfRange(pos, pos + len)
        pos += len
        return bytes.decodeToString()
    }

    fun taggedValue(): Any? {
        val type = data[pos++]
        return when (type) {
            TYPE_INT    -> int()
            TYPE_LONG   -> long()
            TYPE_FLOAT  -> Float.fromBits(int())
            TYPE_DOUBLE -> Double.fromBits(long())
            TYPE_BOOL   -> (data[pos++] != 0.toByte())
            TYPE_STRING -> string()
            else -> throw IllegalArgumentException("Unknown GraphBinary type tag: 0x${type.toString(16)}")
        }
    }
}

// ── Public API ────────────────────────────────────────────────────────────────

fun writeValue(value: Any?): ByteArray {
    val buf = mutableListOf<Byte>()
    buf.addTaggedValue(value)
    return buf.toByteArray()
}

fun readValue(data: ByteArray): Any? = Reader(data).taggedValue()

fun writeGraph(graph: TinkerCat): ByteArray {
    val buf = mutableListOf<Byte>()

    buf.addInt(graph.vertices.size)
    for ((_, vertex) in graph.vertices) {
        buf.addLong(vertex.id() as Long)
        buf.addString(vertex.label())
        val keys = vertex.keys().toList()
        buf.addInt(keys.size)
        for (key in keys) {
            buf.addString(key)
            buf.addTaggedValue(vertex.value<Any?>(key))
        }
    }

    buf.addInt(graph.edges.size)
    for ((_, edge) in graph.edges) {
        buf.addLong(edge.id() as Long)
        buf.addLong(edge.outVertex().id() as Long)
        buf.addLong(edge.inVertex().id() as Long)
        buf.addString(edge.label())
        val keys = edge.keys().toList()
        buf.addInt(keys.size)
        for (key in keys) {
            buf.addString(key)
            buf.addTaggedValue(edge.value<Any?>(key))
        }
    }

    return buf.toByteArray()
}

fun readGraph(data: ByteArray): TinkerCat {
    val r = Reader(data)
    val graph = TinkerCat.open()

    val vCount = r.int()
    repeat(vCount) {
        val id    = r.long()
        val label = r.string()
        val propCount = r.int()
        val args = mutableListOf<Any?>("id", id, "label", label)
        repeat(propCount) {
            args.add(r.string())
            args.add(r.taggedValue())
        }
        graph.addVertex(*args.toTypedArray())
    }

    val eCount = r.int()
    repeat(eCount) {
        val id    = r.long()
        val outId = r.long()
        val inId  = r.long()
        val label = r.string()
        val propCount = r.int()
        val args = mutableListOf<Any?>("id", id)
        repeat(propCount) {
            args.add(r.string())
            args.add(r.taggedValue())
        }
        val outV = graph.vertex(outId) as? TinkerVertex
            ?: throw IllegalStateException("Vertex with id $outId not found during graph deserialization")
        val inV = graph.vertex(inId)
            ?: throw IllegalStateException("Vertex with id $inId not found during graph deserialization")
        outV.addEdge(label, inV, *args.toTypedArray())
    }

    return graph
}
