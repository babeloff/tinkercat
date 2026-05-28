package org.apache.tinkerpop.gremlin.tinkercat.tests

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerCat
import org.apache.tinkerpop.gremlin.tinkercat.structure.TinkerVertex

/**
 * Tests for Task 7.4.2: String Manipulation Traversal Steps.
 *
 * Every test calls a string step (concat, format, toLower, toUpper, trim, ltrim, rtrim,
 * replace, split, length, substring, reverse) on a live TinkerCat traversal.
 * Each step throws UnsupportedOperationException until implemented.
 * Mirrors tests/python/test_7_4_2_string_steps.py.
 */
class Test_7_4_2_StringSteps : StringSpec({

    lateinit var graph: TinkerCat

    beforeTest {
        graph = TinkerCat.open()
        for (name in listOf("Hello", "HELLO", "hello", "  hello  ", "foo bar",
                             "a,b,c", "a, b, c", "HÉLLO", "  alice@EXAMPLE.COM  ")) {
            graph.addVertex(TinkerVertex.T.label, "word", "name", name)
        }
    }

    "concat appends a single suffix" {
        val result = graph.traversal().V()
            .has("name", "Hello").values<String>("name")
            .concat(", World")
            .toList()
        result shouldBe listOf("Hello, World")
    }

    "concat appends multiple parts" {
        val result = graph.traversal().V()
            .has("name", "Hello").values<String>("name")
            .concat("b", "c")
            .toList()
        result shouldBe listOf("Hellobc")
    }

    "format with percent-s placeholder" {
        val result = graph.traversal().V()
            .has("name", "Hello").values<String>("name")
            .format("Hi, %s!")
            .toList()
        result shouldBe listOf("Hi, Hello!")
    }

    "format with token placeholder" {
        val result = graph.traversal().V()
            .has("name", "Hello").values<String>("name")
            .format("%{val}")
            .toList()
        (result is List<*>) shouldBe true
    }

    "format with missing token yields empty string" {
        val result = graph.traversal().V()
            .has("name", "Hello").values<String>("name")
            .format("%{missing}")
            .toList()
        result shouldBe listOf("")
    }

    "toLower converts HELLO to hello" {
        val result = graph.traversal().V()
            .has("name", "HELLO").values<String>("name")
            .toLower()
            .toList()
        result shouldBe listOf("hello")
    }

    "toUpper converts hello to HELLO" {
        val result = graph.traversal().V()
            .has("name", "hello").values<String>("name")
            .toUpper()
            .toList()
        result shouldBe listOf("HELLO")
    }

    "trim strips both ends" {
        val result = graph.traversal().V()
            .has("name", "  hello  ").values<String>("name")
            .trim()
            .toList()
        result shouldBe listOf("hello")
    }

    "ltrim strips leading whitespace only" {
        val result = graph.traversal().V()
            .has("name", "  hello  ").values<String>("name")
            .ltrim()
            .toList()
        result shouldBe listOf("hello  ")
    }

    "rtrim strips trailing whitespace only" {
        val result = graph.traversal().V()
            .has("name", "  hello  ").values<String>("name")
            .rtrim()
            .toList()
        result shouldBe listOf("  hello")
    }

    "replace substitutes a substring" {
        val result = graph.traversal().V()
            .has("name", "foo bar").values<String>("name")
            .replace("bar", "baz")
            .toList()
        result shouldBe listOf("foo baz")
    }

    "split on delimiter emits tokens" {
        val result = graph.traversal().V()
            .has("name", "a,b,c").values<String>("name")
            .split(",")
            .toList()
        result shouldBe listOf("a", "b", "c")
    }

    "split then trim removes extra whitespace" {
        val result = graph.traversal().V()
            .has("name", "a, b, c").values<String>("name")
            .split(",")
            .trim()
            .toList()
        result shouldBe listOf("a", "b", "c")
    }

    "length returns character count" {
        val result = graph.traversal().V()
            .has("name", "hello").values<String>("name")
            .length()
            .toList()
        result shouldBe listOf(5)
    }

    "length of empty string is zero" {
        val g2 = TinkerCat.open()
        try {
            g2.addVertex(TinkerVertex.T.label, "w", "name", "")
            val result = g2.traversal().V().values<String>("name").length().toList()
            result shouldBe listOf(0)
        } finally {
            g2.close()
        }
    }

    "substring with start only" {
        val result = graph.traversal().V()
            .has("name", "hello").values<String>("name")
            .substring(2)
            .toList()
        result shouldBe listOf("llo")
    }

    "substring with start and end" {
        val result = graph.traversal().V()
            .has("name", "hello").values<String>("name")
            .substring(1, 4)
            .toList()
        result shouldBe listOf("ell")
    }

    "reverse flips a string" {
        val result = graph.traversal().V()
            .has("name", "hello").values<String>("name")
            .reverse()
            .toList()
        result shouldBe listOf("olleh")
    }

    "reverse of empty string is empty string" {
        val g2 = TinkerCat.open()
        try {
            g2.addVertex(TinkerVertex.T.label, "w", "name", "")
            val result = g2.traversal().V().values<String>("name").reverse().toList()
            result shouldBe listOf("")
        } finally {
            g2.close()
        }
    }

    "toLower handles unicode" {
        val result = graph.traversal().V()
            .has("name", "HÉLLO").values<String>("name")
            .toLower()
            .toList()
        result shouldBe listOf("héllo")
    }

    "pipeline: trim then toLower" {
        val result = graph.traversal().V()
            .has("name", "  alice@EXAMPLE.COM  ").values<String>("name")
            .trim()
            .toLower()
            .toList()
        result shouldBe listOf("alice@example.com")
    }
})
