package org.apache.tinkerpop.gremlin.process.traversal

/**
 * Tokens that denote different periods of time.
 * Used with the [GraphTraversal.dateAdd] step.
 *
 * Mirrors TinkerPop's `DT` enum (introduced in 3.7.1).
 */
enum class DT {
    second,
    minute,
    hour,
    day
}
