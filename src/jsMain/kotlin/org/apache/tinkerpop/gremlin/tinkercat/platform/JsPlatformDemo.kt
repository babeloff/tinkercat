package org.apache.tinkerpop.gremlin.tinkercat.platform

import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.javascript.TinkerCatJSAdapter
import kotlinx.coroutines.*
import kotlin.js.Promise

/**
 * Interactive demo showcasing TinkerCat JavaScript platform capabilities.
 *
 * Run this to see JS-specific features in action with real-time output.
 * For automated testing, see JavaScript tests in the test directory.
 *
 * Usage: Run `pixi run gradle jsBrowserDevelopmentRun` or `pixi run gradle jsNodeDevelopmentRun`
 */
object JsPlatformDemo {

    fun runDemo() {
        println("🌐 TinkerCat JavaScript Platform Demo")
        println("======================================")

        detectJavaScriptEnvironment()
        demoBasicJavaScriptAPI()
        demoAsyncOperations()
        demoStorageCapabilities()
        demoBrowserSpecificFeatures()
        demoPerformanceShowcase()

        println("\n✅ JavaScript demo completed! Check JS tests for automated testing.")
    }

    private fun detectJavaScriptEnvironment() {
        println("\n🔍 JavaScript Environment Detection")
        println("-".repeat(40))

        val isNode = js("typeof process !== 'undefined' && process.versions && process.versions.node")
        val isBrowser = js("typeof window !== 'undefined'")

        when {
            isNode == true -> {
                println("🟢 Running in Node.js environment")
                val nodeVersion = js("process.versions.node")
                println("📦 Node.js version: $nodeVersion")
            }
            isBrowser == true -> {
                println("🌐 Running in Browser environment")
                val userAgent = js("navigator.userAgent")
                println("🖥️  User Agent: $userAgent")
            }
            else -> {
                println("❓ Unknown JavaScript environment")
            }
        }
    }

    private fun demoBasicJavaScriptAPI() {
        println("\n📊 JavaScript API Demo")
        println("-".repeat(28))

        // Create graph with JS adapter
        val graph = TinkerCat.open()
        val jsAdapter = TinkerCatJSAdapter(graph)

        // Create vertices with dynamic properties (JS-style)
        val alice = jsAdapter.addVertex("person", js("{name: 'Alice', age: 30, skills: ['Kotlin', 'JavaScript']}"))
        val bob = jsAdapter.addVertex("person", js("{name: 'Bob', age: 25, location: 'San Francisco'}"))

        // Create edge with dynamic properties
        val knows = jsAdapter.addEdge(alice, "knows", bob, js("{since: '2020', strength: 0.9}"))

        println("✓ Created graph using JavaScript-friendly API")
        println("✓ Alice (${alice.value<Int>("age")}) knows Bob (${bob.value<Int>("age")})")
        println("✓ Edge properties: since=${knows.value<String>("since")}, strength=${knows.value<Double>("strength")}")

        // Demonstrate JSON serialization
        val graphJson = jsAdapter.toJSON()
        println("✓ Exported graph to JSON (${graphJson.length} characters)")
    }

    private fun demoAsyncOperations() {
        println("\n⚡ Async Operations Demo")
        println("-".repeat(30))

        // Simulate async graph operations
        println("🔄 Starting async graph operations...")

        // TODO: Promise-based operations disabled due to compilation issues
        // val asyncResult = createAsyncGraphOperation()

        println("✓ Async operation placeholder (Promise functionality disabled)")
        println("💡 In browser/Node.js, use .then() or await for Promise handling")
    }

    // TODO: Disabled due to compilation issues with Promise in multiplatform context
    // private fun createAsyncGraphOperation(): Promise<String> {
    //     return Promise { resolve, reject ->
    //         // Simulate async work
    //         val graph = TinkerCat.open()
    //
    //         // Add some data
    //         repeat(10) { i ->
    //             val vertex = graph.addVertex("asyncNode")
    //             vertex.property("id", i)
    //             vertex.property("timestamp", js("Date.now()"))
    //         }
    //
    //         val result = "Created ${graph.vertices().asSequence().count()} async vertices"
    //         resolve(result)
    //     }
    // }

    private fun demoStorageCapabilities() {
        println("\n💾 Storage Capabilities Demo")
        println("-".repeat(34))

        val isNode = js("typeof process !== 'undefined'")
        val isBrowser = js("typeof window !== 'undefined'")

        when {
            isBrowser == true -> {
                println("🌐 Browser storage options:")
                demonstrateBrowserStorage()
            }
            isNode == true -> {
                println("📁 Node.js storage options:")
                demonstrateNodeStorage()
            }
            else -> {
                println("💾 Memory storage (fallback)")
                demonstrateMemoryStorage()
            }
        }
    }

    private fun demonstrateBrowserStorage() {
        // Check localStorage availability
        val hasLocalStorage = js("typeof Storage !== 'undefined'")
        if (hasLocalStorage == true) {
            println("✓ localStorage available for graph persistence")

            // Demo localStorage usage
            js("localStorage.setItem('tinkercat-demo', 'Graph data stored!')")
            val stored = js("localStorage.getItem('tinkercat-demo')")
            println("📝 Stored and retrieved: $stored")
        }

        // Check IndexedDB availability
        val hasIndexedDB = js("typeof window.indexedDB !== 'undefined'")
        if (hasIndexedDB == true) {
            println("✓ IndexedDB available for large graph storage")
            println("🗃️  Suitable for storing complete graph databases")
        }
    }

    private fun demonstrateNodeStorage() {
        // In Node.js, we can use filesystem
        println("✓ File system available for graph persistence")
        println("📂 Can store graphs as JSON, GraphSON, or binary")
        println("🔗 Integration with Node.js streams for large datasets")

        // Note: Actual file operations would require fs module binding
        println("💡 Use fs module bindings for actual file I/O")
    }

    private fun demonstrateMemoryStorage() {
        println("✓ In-memory storage active")
        println("⚠️  Data will not persist between sessions")
    }

    private fun demoBrowserSpecificFeatures() {
        println("\n🌐 Browser-Specific Features Demo")
        println("-".repeat(38))

        val isBrowser = js("typeof window !== 'undefined'")
        if (isBrowser == true) {
            // Web Workers capability
            val hasWorkers = js("typeof Worker !== 'undefined'")
            if (hasWorkers == true) {
                println("👷 Web Workers available for background graph processing")
            }

            // Service Worker capability
            val hasServiceWorkers = js("'serviceWorker' in navigator")
            if (hasServiceWorkers == true) {
                println("🔧 Service Workers available for offline graph caching")
            }

            // WebAssembly capability
            val hasWasm = js("typeof WebAssembly !== 'undefined'")
            if (hasWasm == true) {
                println("⚡ WebAssembly available for high-performance algorithms")
            }

            println("🖥️  DOM integration possible for graph visualization")
        } else {
            println("📋 Browser-specific features not available (not in browser)")
        }
    }

    private fun demoPerformanceShowcase() {
        println("\n🚀 JavaScript Performance Showcase")
        println("-".repeat(39))

        val startTime = js("performance.now() || Date.now()") as Double

        // Create performance test graph
        val graph = TinkerCat.open()
        val jsAdapter = TinkerCatJSAdapter(graph)

        // Batch vertex creation
        repeat(50) { i ->
            val vertex = jsAdapter.addVertex("perfTest", js("{}"))

            // Add some connections
            if (i > 0) {
                val prevVertex = graph.vertices().asSequence().drop(i - 1).first() as org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex
                jsAdapter.addEdge(prevVertex, "connects", vertex, js("{}"))
            }
        }

        val creationTime = (js("performance.now() || Date.now()") as Double) - startTime

        // Query performance
        val queryStart = js("performance.now() || Date.now()") as Double
        val vertexCount = graph.vertices().asSequence().count()
        val edgeCount = graph.edges().asSequence().count()
        val queryTime = (js("performance.now() || Date.now()") as Double) - queryStart

        println("📈 Created $vertexCount vertices and $edgeCount edges in ${creationTime.toInt()}ms")
        println("🔍 Queried graph structure in ${queryTime.toInt()}ms")
        println("💡 JavaScript optimizations and JIT compilation active!")

        // Memory usage (if available)
        val hasMemory = js("performance.memory !== undefined")
        if (hasMemory == true) {
            val usedMemory = js("Math.round(performance.memory.usedJSHeapSize / 1024 / 1024)") as Int
            println("🧠 Current memory usage: ${usedMemory}MB")
        }
    }
}

/**
 * Entry point for JavaScript platform demo.
 *
 * Run with: `pixi run gradle jsBrowserDevelopmentRun` (browser)
 * Or: `pixi run gradle jsNodeDevelopmentRun` (Node.js)
 */
fun main() {
    try {
        JsPlatformDemo.runDemo()
    } catch (e: Exception) {
        println("❌ JavaScript demo failed: ${e.message}")
        println("💡 Some features may require specific browser/Node.js APIs")
    }
}
