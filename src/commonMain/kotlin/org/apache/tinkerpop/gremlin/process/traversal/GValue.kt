package org.apache.tinkerpop.gremlin.process.traversal

/**
 * A Gremlin value that wraps either a concrete value or a named parameter reference.
 *
 * Mirrors TinkerPop's `GValue<T>` (introduced in 3.8.0) for use in parameterized traversals,
 * notably the `call()` step's static params argument.
 */
class GValue<out T>(val value: T) {
    companion object {
        fun <T> of(value: T): GValue<T> = GValue(value)
    }

    override fun toString(): String = "GValue($value)"
}
