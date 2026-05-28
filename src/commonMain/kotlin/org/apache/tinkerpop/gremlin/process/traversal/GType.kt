package org.apache.tinkerpop.gremlin.process.traversal

/**
 * Enumeration of Gremlin data types used for type checking and filtering operations.
 *
 * Each [GType] constant represents a specific data type that can be encountered during
 * graph traversals. This enum is primarily used with the `P.typeOf()` predicate to filter
 * values based on their runtime type.
 *
 * Usage example:
 * ```kotlin
 * g.V().values("age").all(P.typeOf(GType.INT))
 * ```
 *
 * Mirrors TinkerPop's `GType` enum (introduced in 3.8.0).
 */
enum class GType {
    BIGDECIMAL,
    BIGINT,
    BINARY,
    BOOLEAN,
    BYTE,
    CHAR,
    DATETIME,
    DOUBLE,
    DURATION,
    EDGE,
    FLOAT,
    GRAPH,
    INT,
    LIST,
    LONG,
    MAP,
    NULL,
    NUMBER,
    PATH,
    PROPERTY,
    SET,
    SHORT,
    STRING,
    TREE,
    UUID,
    VERTEX,
    VPROPERTY;

    /** Returns true if this type represents a numeric value. */
    fun isNumeric(): Boolean = this in setOf(BIGDECIMAL, BIGINT, BYTE, DOUBLE, FLOAT, INT, LONG, NUMBER, SHORT)
}
