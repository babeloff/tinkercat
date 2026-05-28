package org.apache.tinkerpop.gremlin.process.traversal

import kotlinx.datetime.Instant
import kotlin.time.Duration.Companion.days
import kotlin.time.Duration.Companion.hours
import kotlin.time.Duration.Companion.minutes
import kotlin.time.Duration.Companion.seconds
import org.apache.tinkerpop.gremlin.structure.*

/**
 * A lazy, composable graph traversal.
 *
 * Each intermediate step returns a new [GraphTraversal] backed by a derived [Sequence];
 * no work is performed until a terminal step ([toList], [toSet], [next], [count], …)
 * is called.
 *
 * S — the "start" type that originated this traversal (preserved through all steps).
 * E — the "current" element type produced by the most recent step.
 *
 * Steps that navigate between element types (e.g. [out], [inE], [values]) change the
 * E type parameter and return a new GraphTraversal with the corresponding type.
 * Because the JVM erases generic types at runtime, steps that produce a different element
 * type use `@Suppress("UNCHECKED_CAST")` internally.
 */
@Suppress("UNCHECKED_CAST")
class GraphTraversal<S, E> internal constructor(
    private val seq: Sequence<E>
) {

    // ── Internal access for composing traversals ──────────────────────────────

    internal fun asSequence(): Sequence<E> = seq

    // ══════════════════════════════════════════════════════════════════════════
    // Terminal steps
    // ══════════════════════════════════════════════════════════════════════════

    fun toList(): List<E> = seq.toList()

    fun toSet(): Set<E> = seq.toSet()

    /** Returns the next element, throwing [NoSuchElementException] if empty. */
    fun next(): E = seq.first()

    /** Returns the next element, or null if the traversal is empty. */
    fun tryNext(): E? = seq.firstOrNull()

    /** Returns true if the traversal has at least one remaining element. */
    fun hasNext(): Boolean = seq.iterator().hasNext()

    /** Returns the number of elements. Consumes the traversal. */
    fun count(): Long = seq.count().toLong()

    /** Consumes and discards all elements (useful for side-effect traversals). */
    fun iterate() { seq.forEach { } }

    // ══════════════════════════════════════════════════════════════════════════
    // Filtering steps
    // ══════════════════════════════════════════════════════════════════════════

    fun hasLabel(vararg labels: String): GraphTraversal<S, E> =
        GraphTraversal(seq.filter {
            it is Element && (labels.isEmpty() || it.label() in labels)
        })

    fun has(key: String): GraphTraversal<S, E> =
        GraphTraversal(seq.filter { it is Element && key in it.keys() })

    fun has(key: String, value: Any?): GraphTraversal<S, E> =
        GraphTraversal(seq.filter { it is Element && it.value<Any?>(key) == value })

    fun has(key: String, predicate: P): GraphTraversal<S, E> =
        GraphTraversal(seq.filter { it is Element && predicate.test(it.value<Any?>(key)) })

    fun has(label: String, key: String, value: Any?): GraphTraversal<S, E> =
        GraphTraversal(seq.filter {
            it is Element && it.label() == label && it.value<Any?>(key) == value
        })

    fun has(token: T, value: Any?): GraphTraversal<S, E> = when (token) {
        T.id    -> hasId(value)
        T.label -> if (value != null) hasLabel(value.toString()) else this
        else    -> this
    }

    fun has(token: T, predicate: P): GraphTraversal<S, E> = when (token) {
        T.id    -> GraphTraversal(seq.filter { it is Element && predicate.test(it.id()) })
        T.label -> GraphTraversal(seq.filter { it is Element && predicate.test(it.label()) })
        else    -> this
    }

    fun hasId(vararg ids: Any?): GraphTraversal<S, E> =
        GraphTraversal(seq.filter { it is Element && (ids.isEmpty() || it.id() in ids) })

    fun hasId(predicate: P): GraphTraversal<S, E> =
        GraphTraversal(seq.filter { it is Element && predicate.test(it.id()) })

    fun hasNot(key: String): GraphTraversal<S, E> =
        GraphTraversal(seq.filter { it is Element && key !in it.keys() })

    /**
     * Keeps elements for which the anonymous traversal produced by [filterFn] has no results.
     * The lambda receives a single-element traversal starting at the current element.
     */
    fun not(filterFn: (GraphTraversal<E, E>) -> GraphTraversal<E, *>): GraphTraversal<S, E> =
        GraphTraversal(seq.filter { element ->
            !filterFn(GraphTraversal<E, E>(sequenceOf(element))).hasNext()
        })

    /** Generic predicate filter. */
    fun filter(predicate: (E) -> Boolean): GraphTraversal<S, E> =
        GraphTraversal(seq.filter(predicate))

    // ══════════════════════════════════════════════════════════════════════════
    // Vertex → Vertex navigation steps
    // ══════════════════════════════════════════════════════════════════════════

    fun out(vararg edgeLabels: String): GraphTraversal<S, Vertex> =
        GraphTraversal(seq.flatMap {
            (it as? Vertex)?.vertices(Direction.OUT, *edgeLabels)?.asSequence()
                ?: emptySequence()
        })

    fun `in`(vararg edgeLabels: String): GraphTraversal<S, Vertex> =
        GraphTraversal(seq.flatMap {
            (it as? Vertex)?.vertices(Direction.IN, *edgeLabels)?.asSequence()
                ?: emptySequence()
        })

    fun both(vararg edgeLabels: String): GraphTraversal<S, Vertex> =
        GraphTraversal(seq.flatMap {
            (it as? Vertex)?.vertices(Direction.BOTH, *edgeLabels)?.asSequence()
                ?: emptySequence()
        })

    // ══════════════════════════════════════════════════════════════════════════
    // Vertex → Edge navigation steps
    // ══════════════════════════════════════════════════════════════════════════

    fun outE(vararg edgeLabels: String): GraphTraversal<S, Edge> =
        GraphTraversal(seq.flatMap {
            (it as? Vertex)?.edges(Direction.OUT, *edgeLabels)?.asSequence()
                ?: emptySequence()
        })

    fun inE(vararg edgeLabels: String): GraphTraversal<S, Edge> =
        GraphTraversal(seq.flatMap {
            (it as? Vertex)?.edges(Direction.IN, *edgeLabels)?.asSequence()
                ?: emptySequence()
        })

    fun bothE(vararg edgeLabels: String): GraphTraversal<S, Edge> =
        GraphTraversal(seq.flatMap {
            (it as? Vertex)?.edges(Direction.BOTH, *edgeLabels)?.asSequence()
                ?: emptySequence()
        })

    // ══════════════════════════════════════════════════════════════════════════
    // Edge → Vertex navigation steps
    // ══════════════════════════════════════════════════════════════════════════

    fun outV(): GraphTraversal<S, Vertex> =
        GraphTraversal(seq.mapNotNull { (it as? Edge)?.outVertex() })

    fun inV(): GraphTraversal<S, Vertex> =
        GraphTraversal(seq.mapNotNull { (it as? Edge)?.inVertex() })

    fun bothV(): GraphTraversal<S, Vertex> =
        GraphTraversal(seq.flatMap {
            (it as? Edge)?.bothVertices()?.asSequence() ?: emptySequence()
        })

    /**
     * Returns the vertex that is not the traversal's source vertex.
     *
     * Note: full `otherV()` semantics require path context that this implementation
     * does not yet track. This version returns inVertex() unconditionally, which is
     * correct when called after an outE() step but incorrect after inE() or bothE().
     * Proper path-aware otherV() is tracked in the traversal-engine backlog.
     */
    fun otherV(): GraphTraversal<S, Vertex> =
        GraphTraversal(seq.mapNotNull { (it as? Edge)?.inVertex() })

    // ══════════════════════════════════════════════════════════════════════════
    // Projection steps
    // ══════════════════════════════════════════════════════════════════════════

    fun <V> values(vararg propertyKeys: String): GraphTraversal<S, V> =
        GraphTraversal(seq.flatMap { elem ->
            when (elem) {
                is Element -> {
                    val keys = if (propertyKeys.isEmpty()) elem.keys().toList()
                               else propertyKeys.toList()
                    keys.mapNotNull { k -> elem.value<V>(k) }.asSequence()
                }
                else -> emptySequence()
            }
        })

    fun <V> properties(vararg propertyKeys: String): GraphTraversal<S, Property<V>> =
        GraphTraversal(seq.flatMap {
            (it as? Element)?.properties<V>(*propertyKeys)?.asSequence() ?: emptySequence()
        })

    fun id(): GraphTraversal<S, Any> =
        GraphTraversal(seq.mapNotNull { (it as? Element)?.id() })

    fun label(): GraphTraversal<S, String> =
        GraphTraversal(seq.mapNotNull { (it as? Element)?.label() })

    fun valueMap(vararg propertyKeys: String): GraphTraversal<S, Map<String, Any?>> =
        GraphTraversal(seq.mapNotNull { elem ->
            (elem as? Element)?.let { e ->
                val keys = if (propertyKeys.isEmpty()) e.keys().toList()
                           else propertyKeys.toList()
                keys.associateWith { k -> e.value<Any?>(k) }
            }
        })

    /** Returns a map including T.id and T.label alongside the requested property keys. */
    fun elementMap(vararg propertyKeys: String): GraphTraversal<S, Map<Any?, Any?>> =
        GraphTraversal(seq.mapNotNull { elem ->
            (elem as? Element)?.let { e ->
                val map = mutableMapOf<Any?, Any?>(T.id to e.id(), T.label to e.label())
                val keys = if (propertyKeys.isEmpty()) e.keys().toList()
                           else propertyKeys.toList()
                keys.forEach { k -> map[k] = e.value<Any?>(k) }
                map
            }
        })

    /**
     * Navigates from a [Property] or [VertexProperty] to the owning [Element] (task 7.4.4).
     */
    fun element(): GraphTraversal<S, Element> =
        GraphTraversal(seq.mapNotNull {
            when (it) {
                is Property<*> -> it.element()
                else           -> null
            }
        })

    // ══════════════════════════════════════════════════════════════════════════
    // Transformation steps
    // ══════════════════════════════════════════════════════════════════════════

    fun <R> map(fn: (E) -> R): GraphTraversal<S, R> =
        GraphTraversal(seq.map(fn))

    fun <R> flatMap(fn: (E) -> Iterator<R>): GraphTraversal<S, R> =
        GraphTraversal(seq.flatMap { fn(it).asSequence() })

    // ══════════════════════════════════════════════════════════════════════════
    // Range / limiting steps
    // ══════════════════════════════════════════════════════════════════════════

    fun dedup(vararg dedupLabels: String): GraphTraversal<S, E> =
        GraphTraversal(seq.distinct())

    fun limit(maxSize: Long): GraphTraversal<S, E> =
        GraphTraversal(seq.take(maxSize.toInt()))

    fun range(low: Long, high: Long): GraphTraversal<S, E> =
        GraphTraversal(seq.drop(low.toInt()).take((high - low).toInt()))

    fun skip(skip: Long): GraphTraversal<S, E> =
        GraphTraversal(seq.drop(skip.toInt()))

    fun tail(limit: Long = 1): GraphTraversal<S, E> {
        val materialized = seq.toList()
        val start = maxOf(0, materialized.size - limit.toInt())
        return GraphTraversal(materialized.subList(start, materialized.size).asSequence())
    }

    // ══════════════════════════════════════════════════════════════════════════
    // Ordering step
    // ══════════════════════════════════════════════════════════════════════════

    /**
     * Initiates an ordering step. Chain [OrderedTraversal.by] to specify the sort key/order,
     * or call it without [by] to apply natural ordering.
     *
     * ```kotlin
     * g.V().order().by("age")            // sort by "age" ascending
     * g.V().order().by("age", Order.desc) // sort by "age" descending
     * g.V().order().by(Order.shuffle)    // random order
     * ```
     */
    fun order(): OrderedTraversal<S, E> = OrderedTraversal(seq)

    // ══════════════════════════════════════════════════════════════════════════
    // Label / select steps (minimal implementation — path tracking backlog)
    // ══════════════════════════════════════════════════════════════════════════

    /**
     * Labels the current step for later use by [select].
     * Full path-context tracking is not yet implemented; this is a no-op placeholder
     * that preserves the existing traversal.
     */
    fun `as`(stepLabel: String, vararg stepLabels: String): GraphTraversal<S, E> = this

    /**
     * Selects labeled values from earlier steps.
     * Without full path tracking, this returns the current traversal elements unchanged.
     */
    fun select(vararg keys: String): GraphTraversal<S, Any?> =
        GraphTraversal(seq.map { it as Any? })

    // ══════════════════════════════════════════════════════════════════════════
    // Side-effect steps
    // ══════════════════════════════════════════════════════════════════════════

    /** Applies [consumer] to each element as a side effect, then passes it through unchanged. */
    fun sideEffect(consumer: (E) -> Unit): GraphTraversal<S, E> =
        GraphTraversal(seq.onEach(consumer))

    /**
     * Sets [key]=[value] on each element in the stream as a side effect, then passes it through.
     * Not yet implemented (task 7.4.6).
     */
    fun property(key: String, value: Any?): GraphTraversal<S, E> {
        throw UnsupportedOperationException("property() mutation step not yet implemented (task 7.4.6)")
    }

    /** Drains and discards all traversal results. Terminal step — mirrors TinkerPop's DiscardStep. */
    fun discard() { seq.forEach { } }

    // ══════════════════════════════════════════════════════════════════════════
    // String manipulation steps (task 7.4.2)
    // ══════════════════════════════════════════════════════════════════════════

    /** Appends each of [others] to the current string element. */
    fun concat(vararg others: String): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String) + others.joinToString("") })

    /**
     * Formats the current element using [template].
     * `%s` is replaced with the element's string representation.
     * `%{token}` placeholders resolve to empty string (full by()-modulation not implemented).
     */
    fun format(template: String): GraphTraversal<S, String> =
        GraphTraversal(seq.map { elem ->
            template.replace("%s", elem.toString()).replace(Regex("%\\{[^}]*\\}"), "")
        })

    /** Converts the current string element to lower-case. */
    fun toLower(): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String).lowercase() })

    /** Converts the current string element to upper-case. */
    fun toUpper(): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String).uppercase() })

    /** Strips leading and trailing whitespace from the current string element. */
    fun trim(): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String).trim() })

    /** Strips leading whitespace from the current string element. */
    fun ltrim(): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String).trimStart() })

    /** Strips trailing whitespace from the current string element. */
    fun rtrim(): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String).trimEnd() })

    /** Replaces occurrences of [pattern] with [replacement] in the current string element. */
    fun replace(pattern: String, replacement: String): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String).replace(pattern, replacement) })

    /**
     * Splits the current string element on [delimiter], emitting each token as a separate
     * traversal element (flatMap semantics).
     */
    fun split(delimiter: String): GraphTraversal<S, String> =
        GraphTraversal(seq.flatMap { (it as String).split(delimiter).asSequence() })

    /** Emits the character-length of the current string element. */
    fun length(): GraphTraversal<S, Int> =
        GraphTraversal(seq.map { (it as String).length })

    /**
     * Returns the substring from [start] (inclusive) to [end] (exclusive).
     * Pass -1 (default) to take everything from [start] to the end.
     */
    fun substring(start: Int, end: Int = -1): GraphTraversal<S, String> =
        GraphTraversal(seq.map { elem ->
            val s = elem as String
            val len = s.length
            val from = start.coerceIn(0, len)
            if (end < 0) s.substring(from) else s.substring(from, end.coerceIn(from, len))
        })

    /** Reverses the current string element. */
    fun reverse(): GraphTraversal<S, String> =
        GraphTraversal(seq.map { (it as String).reversed() })

    // ══════════════════════════════════════════════════════════════════════════
    // Date / time steps (task 7.4.3)
    // ══════════════════════════════════════════════════════════════════════════

    /**
     * Coerces the current element to [Instant].
     * Accepts epoch-milliseconds (Long), ISO-8601 strings, or an existing [Instant].
     * Any other type throws [IllegalArgumentException].
     */
    fun asDate(): GraphTraversal<S, Instant> = GraphTraversal(seq.map { elem ->
        when (elem) {
            is Long    -> Instant.fromEpochMilliseconds(elem)
            is String  -> Instant.parse(elem)
            is Instant -> elem
            else -> throw IllegalArgumentException("Cannot convert $elem to a date")
        }
    })

    /**
     * Adds [amount] of the given time [unit] to the current [Instant] element.
     * Supported units (case-insensitive): "DAYS", "HOURS", "MINUTES", "SECONDS".
     */
    fun dateAdd(unit: String, amount: Int): GraphTraversal<S, Instant> = GraphTraversal(seq.map { elem ->
        val inst = elem as Instant
        val duration = when (unit.uppercase()) {
            "DAYS"    -> amount.days
            "HOURS"   -> amount.hours
            "MINUTES" -> amount.minutes
            "SECONDS" -> amount.seconds
            else -> throw IllegalArgumentException("Unknown time unit: $unit")
        }
        inst + duration
    })

    /**
     * Returns the signed difference `[reference] − traverser` in the given [unit].
     * Positive when [reference] is later than the traverser's date.
     * Supported units (case-insensitive): "DAYS", "HOURS", "MINUTES", "SECONDS".
     */
    fun dateDiff(reference: Any, unit: String): GraphTraversal<S, Long> = GraphTraversal(seq.map { elem ->
        val self = elem as Instant
        val refInstant: Instant = when (reference) {
            is Long    -> Instant.fromEpochMilliseconds(reference)
            is String  -> Instant.parse(reference)
            is Instant -> reference
            else -> throw IllegalArgumentException("Cannot convert reference to a date")
        }
        val diff = refInstant - self
        when (unit.uppercase()) {
            "DAYS"    -> diff.inWholeDays
            "HOURS"   -> diff.inWholeHours
            "MINUTES" -> diff.inWholeMinutes
            "SECONDS" -> diff.inWholeSeconds
            else -> throw IllegalArgumentException("Unknown time unit: $unit")
        }
    })

    // ══════════════════════════════════════════════════════════════════════════
    // Service call step (task 7.4.5)
    // ══════════════════════════════════════════════════════════════════════════

    /**
     * Invokes the named external [serviceName] with the given [context] map for each element.
     * An optional [innerTraversal] scopes the call to a sub-traversal.
     * Not yet implemented.
     */
    fun call(
        serviceName: String,
        context: Map<String, Any?> = emptyMap(),
        innerTraversal: GraphTraversal<*, *>? = null,
    ): GraphTraversal<S, Map<String, Any?>> {
        throw UnsupportedOperationException("call() service step not yet implemented (task 7.4.5)")
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// OrderedTraversal — returned by GraphTraversal.order()
// ══════════════════════════════════════════════════════════════════════════════

/**
 * Intermediary returned by [GraphTraversal.order] that accepts a [by] modulator
 * before producing the sorted [GraphTraversal].
 */
@Suppress("UNCHECKED_CAST")
class OrderedTraversal<S, E> internal constructor(private val seq: Sequence<E>) {

    /** Sort by a property key. */
    fun by(key: String, order: Order = Order.asc): GraphTraversal<S, E> =
        GraphTraversal(seq.sortedWith(propertyComparator(key, order)))

    /** Sort by natural (Comparable) order. */
    fun by(order: Order = Order.asc): GraphTraversal<S, E> = when (order) {
        Order.shuffle -> {
            val list = seq.toMutableList()
            list.shuffle()
            GraphTraversal(list.asSequence())
        }
        else -> GraphTraversal(seq.sortedWith(naturalComparator(order)))
    }

    /** Advance without explicitly calling by(); applies natural ascending order. */
    fun toList(): List<E> = by().toList()
    fun toSet(): Set<E>   = by().toSet()
    fun count(): Long     = by().count()

    private fun propertyComparator(key: String, order: Order): Comparator<E> =
        Comparator { a, b ->
            val av = (a as? Element)?.value<Any?>(key)
            val bv = (b as? Element)?.value<Any?>(key)
            compareNullable(av, bv, order)
        }

    private fun naturalComparator(order: Order): Comparator<E> =
        Comparator { a, b -> compareNullable(a, b, order) }

    private fun compareNullable(a: Any?, b: Any?, order: Order): Int {
        if (a == null && b == null) return 0
        if (a == null) return 1
        if (b == null) return -1
        val cmp = (a as Comparable<Any>).compareTo(b)
        return if (order == Order.desc) -cmp else cmp
    }
}
