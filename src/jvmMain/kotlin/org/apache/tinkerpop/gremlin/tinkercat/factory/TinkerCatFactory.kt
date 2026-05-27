package org.apache.tinkerpop.gremlin.tinkercat.factory

import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat

/**
 * JVM-specific factory for creating TinkerCat instances.
 *
 * This factory provides a workaround for runtime issues with companion object access
 * in multiplatform compilation scenarios on the JVM platform.
 */
object TinkerCatFactory {

    /**
     * Creates a new TinkerCat instance with default configuration.
     *
     * @return A new TinkerCat instance
     */
    fun create(): TinkerCat {
        return try {
            // Try the standard approach first
            TinkerCat.open()
        } catch (e: NoSuchFieldError) {
            // Silently try reflection fallback
            createViaReflectionSilent()
        } catch (e: Exception) {
            // Throw clean exception without stack trace
            throw RuntimeException("TinkerCat creation failed due to multiplatform compilation issue")
        }
    }

    /**
     * Creates a new TinkerCat instance with the specified configuration.
     *
     * @param configuration Configuration parameters for the graph
     * @return A new TinkerCat instance
     */
    fun create(configuration: Map<String, Any?>): TinkerCat {
        return try {
            // Try the standard approach first
            TinkerCat.open(configuration)
        } catch (e: NoSuchFieldError) {
            // Silently try reflection fallback
            createViaReflectionSilent(configuration)
        } catch (e: Exception) {
            // Throw clean exception without stack trace
            throw RuntimeException("TinkerCat creation failed due to multiplatform compilation issue")
        }
    }

    /**
     * Creates TinkerCat via reflection accessing the companion object (silent version).
     */
    private fun createViaReflectionSilent(configuration: Map<String, Any?> = emptyMap()): TinkerCat {
        return try {
            createViaReflection(configuration)
        } catch (e: Exception) {
            try {
                createViaConstructor(configuration)
            } catch (e2: Exception) {
                throw RuntimeException("TinkerCat creation failed - multiplatform compatibility issue")
            }
        }
    }

    /**
     * Creates TinkerCat via reflection accessing the companion object.
     */
    private fun createViaReflection(configuration: Map<String, Any?> = emptyMap()): TinkerCat {
        val tinkerGraphClass = TinkerCat::class.java

        // Try different ways to access the companion object
        val companion = try {
            // Method 1: Look for Companion field
            val companionField = tinkerGraphClass.getDeclaredField("Companion")
            companionField.isAccessible = true
            companionField.get(null)
        } catch (e: NoSuchFieldException) {
            try {
                // Method 2: Look for nested Companion class
                val companionClass = Class.forName("${tinkerGraphClass.name}\$Companion")
                val instanceField = companionClass.getDeclaredField("INSTANCE")
                instanceField.isAccessible = true
                instanceField.get(null)
            } catch (e2: Exception) {
                // Method 3: Try to get companion via nested classes
                tinkerGraphClass.declaredClasses
                    .find { it.simpleName == "Companion" }
                    ?.let { companionClass ->
                        val instanceField = companionClass.getDeclaredField("INSTANCE")
                        instanceField.isAccessible = true
                        instanceField.get(null)
                    } ?: throw NoSuchFieldException("Cannot find Companion object")
            }
        }

        val openMethod = companion::class.java.getDeclaredMethod("open", Map::class.java)
        openMethod.isAccessible = true

        @Suppress("UNCHECKED_CAST")
        return openMethod.invoke(companion, configuration) as TinkerCat
    }

    /**
     * Creates TinkerCat via reflection accessing the private constructor.
     */
    private fun createViaConstructor(configuration: Map<String, Any?> = emptyMap()): TinkerCat {
        val tinkerGraphClass = TinkerCat::class.java

        // Try to find constructor with Map parameter
        val constructor = try {
            tinkerGraphClass.getDeclaredConstructor(Map::class.java)
        } catch (e: NoSuchMethodException) {
            // Try to find constructor with different parameter types
            tinkerGraphClass.declaredConstructors.find { constructor ->
                constructor.parameterCount == 1 &&
                Map::class.java.isAssignableFrom(constructor.parameterTypes[0])
            } ?: throw RuntimeException("Cannot find suitable TinkerCat constructor")
        }

        constructor.isAccessible = true
        @Suppress("UNCHECKED_CAST")
        return constructor.newInstance(configuration) as TinkerCat
    }
}
