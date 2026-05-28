package org.apache.tinkerpop.gremlin.process.traversal

/**
 * Tokens that represent access to the internal properties of Element objects.
 * Used as keys in has() predicates and elementMap() results.
 */
enum class T {
    /** The element identifier. */
    id,
    /** The element label. */
    label,
    /** The property key (for VertexProperty traversals). */
    key,
    /** The property value (for VertexProperty traversals). */
    value
}
