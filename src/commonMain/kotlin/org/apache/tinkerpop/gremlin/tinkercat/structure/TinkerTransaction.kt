package org.apache.tinkerpop.gremlin.tinkercat.structure

/**
 * Stub transaction returned by [TinkerCat.tx].
 *
 * ACID transactions are not yet implemented in TinkerCat. Every method throws
 * [UnsupportedOperationException] with a descriptive message so callers receive
 * actionable feedback at runtime. The stub exists in source so that code calling
 * [TinkerCat.tx] compiles and links on all platforms without requiring local
 * workarounds in callers.
 *
 * When transactions are implemented, replace this stub with a real transaction
 * that participates in the graph's storage backend.
 */
class TinkerTransaction : AutoCloseable {

    fun open(): Nothing = throw UnsupportedOperationException(
        "TinkerCat does not yet implement ACID transactions. " +
        "open() is a stub — see the issue tracker to follow progress."
    )

    fun commit(): Nothing = throw UnsupportedOperationException(
        "TinkerCat does not yet implement ACID transactions. " +
        "commit() is a stub — see the issue tracker to follow progress."
    )

    fun rollback(): Nothing = throw UnsupportedOperationException(
        "TinkerCat does not yet implement ACID transactions. " +
        "rollback() is a stub — see the issue tracker to follow progress."
    )

    override fun close(): Unit = throw UnsupportedOperationException(
        "TinkerCat does not yet implement ACID transactions. " +
        "close() is a stub — see the issue tracker to follow progress."
    )
}
