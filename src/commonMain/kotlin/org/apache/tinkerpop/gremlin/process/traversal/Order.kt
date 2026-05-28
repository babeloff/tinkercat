package org.apache.tinkerpop.gremlin.process.traversal

/**
 * Defines the order in which traversal results are sorted by the order() step.
 */
enum class Order {
    /** Ascending natural order. */
    asc,
    /** Descending natural order. */
    desc,
    /** Random (shuffle) order. */
    shuffle
}
