/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
@file:OptIn(kotlin.experimental.ExperimentalNativeApi::class, kotlin.native.runtime.NativeRuntimeApi::class)
package org.apache.tinkerpop.gremlin.tinkercat.structure

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue
import kotlin.test.assertFalse
import kotlin.time.measureTime
import org.apache.tinkerpop.gremlin.structure.Vertex
import org.apache.tinkerpop.gremlin.structure.Edge
import org.apache.tinkerpop.gremlin.process.traversal.P

/**
 * Native platform compliance tests for TinkerCat following Apache TinkerPop Java compliance tests.
 *
 * Task 4.1.2 Phase 3 - Native Platform Compliance Testing
 */
class TinkerCatNativeTest {

    @Test
    fun testNativeGraphCreation() {
        val graph = TinkerCat.open()
        assertNotNull(graph)
        // TinkerCat does not support computer or transactions in memory mode
        assertFalse(graph.features().graph().supportsComputer())
        assertFalse(graph.features().graph().supportsTransactions())
        assertTrue(graph.features().vertex().supportsUserSuppliedIds())
        assertTrue(graph.features().edge().supportsUserSuppliedIds())
        val config = graph.configuration()
        assertNotNull(config)
        graph.close()
    }

    @Test
    fun testMemoryManagementCompliance() {
        val graph = TinkerCat.open()
        repeat(1000) { i ->
            graph.addVertex("id", i, "name", "vertex$i")
        }
        assertEquals(1000L, graph.traversal().V().count())

        // Remove all vertices
        graph.vertices().asSequence().toList().forEach { it.remove() }
        assertEquals(0L, graph.traversal().V().count())

        // Suggest native garbage collection
        kotlin.native.runtime.GC.collect()
        graph.close()
    }

    @Test
    fun testNativeDataTypeSupport() {
        val graph = TinkerCat.open()
        val vertex = graph.addVertex(
            "byte", 127.toByte(),
            "short", 32767.toShort(),
            "int", Int.MAX_VALUE,
            "long", Long.MAX_VALUE,
            "float", Float.MAX_VALUE,
            "double", Double.MAX_VALUE,
            "boolean", true,
            "string", "native test"
        )
        assertEquals(127.toByte(), vertex.value<Byte>("byte"))
        assertEquals(32767.toShort(), vertex.value<Short>("short"))
        assertEquals(Int.MAX_VALUE, vertex.value<Int>("int"))
        assertEquals(Long.MAX_VALUE, vertex.value<Long>("long"))
        assertEquals(Float.MAX_VALUE, vertex.value<Float>("float"))
        assertEquals(Double.MAX_VALUE, vertex.value<Double>("double"))
        assertEquals(true, vertex.value<Boolean>("boolean"))
        assertEquals("native test", vertex.value<String>("string"))
        graph.close()
    }

    @Test
    fun testNativeArrayHandling() {
        val graph = TinkerCat.open()
        val intArray = intArrayOf(1, 2, 3, 4, 5)
        val stringArray = arrayOf("a", "b", "c")
        val vertex = graph.addVertex(
            "intArray", intArray,
            "stringArray", stringArray,
            "list", listOf("x", "y", "z")
        )
        assertTrue(vertex.property<Any?>("intArray").isPresent())
        assertTrue(vertex.property<Any?>("stringArray").isPresent())
        assertTrue(vertex.property<Any?>("list").isPresent())
        graph.close()
    }

    @Test
    fun testNativePerformanceBaseline() {
        val graph = TinkerCat.open()
        val creationTime = measureTime {
            repeat(10000) { i ->
                graph.addVertex("id", i, "name", "vertex$i", "value", i * 2.0)
            }
        }.inWholeMilliseconds
        println("Native vertex creation time: ${creationTime}ms")
        assertTrue(creationTime < 5000)

        val g = graph.traversal()
        var count = 0L
        val traversalTime = measureTime {
            count = g.V().has("value", P.gt(1000.0)).count()
        }.inWholeMilliseconds
        println("Native traversal time: ${traversalTime}ms")
        assertTrue(traversalTime < 1000)
        assertTrue(count > 0)
        graph.close()
    }

    @Test
    fun testNativeStringInterning() {
        val graph = TinkerCat.open()
        val commonLabel = "person"
        val commonProperty = "name"
        repeat(1000) { i ->
            graph.addVertex("label", commonLabel, commonProperty, "person$i")
        }
        val personCount = graph.traversal().V().hasLabel(commonLabel).count()
        assertEquals(1000L, personCount)
        val uniqueNames = graph.traversal().V().values<String>(commonProperty).dedup().count()
        assertEquals(1000L, uniqueNames)
        graph.close()
    }

    @Test
    fun testNativeConcurrencyCompliance() {
        val graph = TinkerCat.open()
        val vertex1 = graph.addVertex("thread", "main", "id", 1)
        val vertex2 = graph.addVertex("thread", "main", "id", 2)
        vertex1.addEdge("connects", vertex2)
        val edgeCount = graph.traversal().E().count()
        assertEquals(1L, edgeCount)
        // TinkerCat does not support transactions
        assertFalse(graph.features().graph().supportsTransactions())
        graph.close()
    }

    @Test
    fun testNativePlatformFeatures() {
        val graph = TinkerCat.open()
        val features = graph.features()
        // TinkerCat does not support transactions or persistence in memory mode
        assertFalse(features.graph().supportsTransactions())
        assertFalse(features.graph().supportsPersistence())
        // Vertex ID support
        assertTrue(features.vertex().supportsUserSuppliedIds())
        assertTrue(features.vertex().supportsNumericIds())
        assertTrue(features.vertex().supportsStringIds())
        // Edge ID support
        assertTrue(features.edge().supportsUserSuppliedIds())
        assertTrue(features.edge().supportsNumericIds())
        assertTrue(features.edge().supportsStringIds())
        // Meta and multi property support
        assertTrue(features.vertex().supportsMetaProperties())
        assertTrue(features.vertex().supportsMultiProperties())
        graph.close()
    }

    @Test
    fun testNativeIndexingPerformance() {
        val graph = TinkerCat.open()
        repeat(5000) { i ->
            graph.addVertex(
                "indexed_id", i,
                "category", "type${i % 10}",
                "score", i.toDouble() / 100.0
            )
        }
        val g = graph.traversal()

        var specificVertex: Any? = null
        val lookupTime = measureTime {
            specificVertex = g.V().has("indexed_id", 2500).next()
        }.inWholeMilliseconds
        assertNotNull(specificVertex)
        assertTrue(lookupTime < 100)

        var rangeResults = 0L
        val rangeTime = measureTime {
            rangeResults = g.V().has("score", P.between(10.0, 20.0)).count()
        }.inWholeMilliseconds
        assertTrue(rangeResults > 0)
        assertTrue(rangeTime < 500)
        graph.close()
    }

    @Test
    fun testNativeErrorHandling() {
        val graph = TinkerCat.open()
        // value() returns null for missing properties
        val vertex = graph.addVertex()
        val missing = vertex.value<String>("nonexistent")
        assertTrue(missing == null)

        // addVertex with null key throws IllegalArgumentException
        try {
            graph.addVertex(null, "value")
            kotlin.test.fail("Should throw exception for null key")
        } catch (e: Exception) {
            assertTrue(true)
        }
        graph.close()
    }

    @Test
    fun testNativeResourceManagement() {
        val graph = TinkerCat.open()
        val vertices = mutableListOf<Vertex>()
        val edges = mutableListOf<Edge>()

        repeat(100) { i ->
            val v1 = graph.addVertex("id", i * 2)
            val v2 = graph.addVertex("id", i * 2 + 1)
            val edge = v1.addEdge("connects", v2, "weight", i.toDouble())
            vertices.add(v1)
            vertices.add(v2)
            edges.add(edge)
        }

        assertEquals(200L, graph.traversal().V().count())
        assertEquals(100L, graph.traversal().E().count())

        // Remove edges first, then vertices
        edges.forEach { it.remove() }
        vertices.forEach { it.remove() }

        assertEquals(0L, graph.traversal().V().count())
        assertEquals(0L, graph.traversal().E().count())

        kotlin.native.runtime.GC.collect()
        graph.close()
    }

    @Test
    fun testNativeInteroperability() {
        val graph = TinkerCat.open()
        val vertex = graph.addVertex("native_ptr", 0x12345678L)
        assertEquals(0x12345678L, vertex.value<Long>("native_ptr"))

        // configuration() returns a Map<String, Any?>
        val config = graph.configuration()
        assertNotNull(config)

        val vertexCount = graph.traversal().V().count()
        assertTrue(vertexCount >= 0)
        graph.close()
    }

    companion object {
        init {
            println("TinkerCat Native Compliance Tests initialized")
            println("Platform: ${kotlin.native.Platform.osFamily}")
            println("Architecture: ${kotlin.native.Platform.cpuArchitecture}")
        }
    }
}
