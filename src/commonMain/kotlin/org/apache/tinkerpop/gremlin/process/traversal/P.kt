package org.apache.tinkerpop.gremlin.process.traversal

/**
 * A predicate used in has() and other filter steps to express conditions on property values.
 *
 * P wraps a boolean test function and an optional reference value. Predicates can be
 * negated, combined with and()/or(), or constructed via the factory methods on the
 * companion object.
 *
 * String predicates (startingWith, endingWith, containing, regexp) were added for
 * TinkerPop 3.8.x / Gremlin 4.0 parity (task 7.7.2).
 */
class P private constructor(
    val value: Any?,
    private val testFn: (Any?) -> Boolean
) {

    fun test(v: Any?): Boolean = testFn(v)

    fun negate(): P = P(value) { !testFn(it) }

    fun and(other: P): P = P(value) { testFn(it) && other.testFn(it) }

    fun or(other: P): P = P(value) { testFn(it) || other.testFn(it) }

    companion object {

        // ── Equality ──────────────────────────────────────────────────────────

        fun eq(value: Any?): P = P(value) { it == value }

        fun neq(value: Any?): P = P(value) { it != value }

        // ── Ordering (Comparable values) ──────────────────────────────────────

        @Suppress("UNCHECKED_CAST")
        fun lt(value: Any): P = P(value) { v ->
            v != null && (v as Comparable<Any>).compareTo(value) < 0
        }

        @Suppress("UNCHECKED_CAST")
        fun lte(value: Any): P = P(value) { v ->
            v != null && (v as Comparable<Any>).compareTo(value) <= 0
        }

        @Suppress("UNCHECKED_CAST")
        fun gt(value: Any): P = P(value) { v ->
            v != null && (v as Comparable<Any>).compareTo(value) > 0
        }

        @Suppress("UNCHECKED_CAST")
        fun gte(value: Any): P = P(value) { v ->
            v != null && (v as Comparable<Any>).compareTo(value) >= 0
        }

        // ── Range ─────────────────────────────────────────────────────────────

        /** Inclusive lower bound, exclusive upper bound: [min, max). */
        @Suppress("UNCHECKED_CAST")
        fun between(min: Any, max: Any): P = P(min) { v ->
            v != null &&
                (v as Comparable<Any>).compareTo(min) >= 0 &&
                (v as Comparable<Any>).compareTo(max) < 0
        }

        /** Strictly between (exclusive on both ends): (min, max). */
        @Suppress("UNCHECKED_CAST")
        fun inside(min: Any, max: Any): P = P(min) { v ->
            v != null &&
                (v as Comparable<Any>).compareTo(min) > 0 &&
                (v as Comparable<Any>).compareTo(max) < 0
        }

        /** Outside the range: v < min || v > max. */
        @Suppress("UNCHECKED_CAST")
        fun outside(min: Any, max: Any): P = P(min) { v ->
            v != null &&
                ((v as Comparable<Any>).compareTo(min) < 0 ||
                    (v as Comparable<Any>).compareTo(max) > 0)
        }

        // ── Set membership ────────────────────────────────────────────────────

        fun within(vararg values: Any?): P = P(values) { it in values }

        fun within(values: Collection<Any?>): P = P(values) { it in values }

        fun without(vararg values: Any?): P = P(values) { it !in values }

        fun without(values: Collection<Any?>): P = P(values) { it !in values }

        // ── Negation ──────────────────────────────────────────────────────────

        fun not(predicate: P): P = predicate.negate()

        // ── String predicates (task 7.7.2) ────────────────────────────────────

        fun startingWith(prefix: String): P = P(prefix) { v ->
            v is String && v.startsWith(prefix)
        }

        fun notStartingWith(prefix: String): P = P(prefix) { v ->
            v is String && !v.startsWith(prefix)
        }

        fun endingWith(suffix: String): P = P(suffix) { v ->
            v is String && v.endsWith(suffix)
        }

        fun notEndingWith(suffix: String): P = P(suffix) { v ->
            v is String && !v.endsWith(suffix)
        }

        fun containing(substring: String): P = P(substring) { v ->
            v is String && v.contains(substring)
        }

        fun notContaining(substring: String): P = P(substring) { v ->
            v is String && !v.contains(substring)
        }

        fun regexp(pattern: String): P = P(pattern) { v ->
            v is String && Regex(pattern).containsMatchIn(v)
        }
    }
}
