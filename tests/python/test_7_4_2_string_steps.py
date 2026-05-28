"""
Tests for Task 7.4.2: String Manipulation Traversal Steps.

All tests call string steps (concat, toLower, toUpper, trim, replace,
split, length, substring, reverse, format) on a live TinkerCat traversal.
None of these steps are implemented yet; every test fails with
AttributeError until they are added to TinkerCat's GraphTraversal.
See docs/project/changelog/task-7.4.2-string-steps.adoc.
"""

import pytest

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    graph.add_vertex("word", name="Hello")
    graph.add_vertex("word", name="HELLO")
    graph.add_vertex("word", name="hello")
    graph.add_vertex("word", name="  hello  ")
    graph.add_vertex("word", name="foo bar")
    graph.add_vertex("word", name="a,b,c")
    graph.add_vertex("word", name="a, b, c")
    graph.add_vertex("word", name="HÉLLO")
    graph.add_vertex("word", name="  alice@EXAMPLE.COM  ")
    yield graph
    graph.close()


def test_concat(g):
    result = g.traversal().V().has("name", "Hello").values("name").concat(", World").to_list()  # AttributeError
    assert result == ["Hello, World"]


def test_concat_multiple(g):
    result = g.traversal().V().has("name", "Hello").values("name").concat("b", "c").to_list()  # AttributeError
    assert result == ["Hellobc"]


def test_format_percent_s(g):
    result = g.traversal().V().has("name", "Hello").values("name").format("Hi, %s!").to_list()  # AttributeError
    assert result == ["Hi, Hello!"]


def test_format_tokens(g):
    result = g.traversal().V().has("name", "Hello").values("name").format("%{val}").to_list()  # AttributeError
    assert isinstance(result, list)


def test_format_missing_token_empty(g):
    result = g.traversal().V().has("name", "Hello").values("name").format("%{missing}").to_list()  # AttributeError
    assert result == [""]


def test_to_lower(g):
    result = g.traversal().V().has("name", "HELLO").values("name").to_lower().to_list()  # AttributeError
    assert result == ["hello"]


def test_to_upper(g):
    result = g.traversal().V().has("name", "hello").values("name").to_upper().to_list()  # AttributeError
    assert result == ["HELLO"]


def test_trim(g):
    result = g.traversal().V().has("name", "  hello  ").values("name").trim().to_list()  # AttributeError
    assert result == ["hello"]


def test_ltrim(g):
    result = g.traversal().V().has("name", "  hello  ").values("name").ltrim().to_list()  # AttributeError
    assert result == ["hello  "]


def test_rtrim(g):
    result = g.traversal().V().has("name", "  hello  ").values("name").rtrim().to_list()  # AttributeError
    assert result == ["  hello"]


def test_replace(g):
    result = g.traversal().V().has("name", "foo bar").values("name").replace("bar", "baz").to_list()  # AttributeError
    assert result == ["foo baz"]


def test_split_delimiter(g):
    result = g.traversal().V().has("name", "a,b,c").values("name").split(",").to_list()  # AttributeError
    assert result == ["a", "b", "c"]


def test_split_then_trim(g):
    result = g.traversal().V().has("name", "a, b, c").values("name").split(",").trim().to_list()  # AttributeError
    assert result == ["a", "b", "c"]


def test_length(g):
    result = g.traversal().V().has("name", "hello").values("name").length().to_list()  # AttributeError
    assert result == [5]


def test_length_empty_string():
    g = TinkerCat()
    try:
        g.add_vertex("w", name="")
        result = g.traversal().V().values("name").length().to_list()  # AttributeError
        assert result == [0]
    finally:
        g.close()


def test_substring_start_only(g):
    result = g.traversal().V().has("name", "hello").values("name").substring(2).to_list()  # AttributeError
    assert result == ["llo"]


def test_substring_start_end(g):
    result = g.traversal().V().has("name", "hello").values("name").substring(1, 4).to_list()  # AttributeError
    assert result == ["ell"]


def test_reverse(g):
    result = g.traversal().V().has("name", "hello").values("name").reverse().to_list()  # AttributeError
    assert result == ["olleh"]


def test_reverse_empty():
    g = TinkerCat()
    try:
        g.add_vertex("w", name="")
        result = g.traversal().V().values("name").reverse().to_list()  # AttributeError
        assert result == [""]
    finally:
        g.close()


def test_unicode_to_lower(g):
    result = g.traversal().V().has("name", "HÉLLO").values("name").to_lower().to_list()  # AttributeError
    assert result == ["héllo"]


def test_pipeline_composition(g):
    result = (
        g.traversal().V()
        .has("name", "  alice@EXAMPLE.COM  ")
        .values("name")
        .trim()
        .to_lower()
        .to_list()  # AttributeError
    )
    assert result == ["alice@example.com"]
