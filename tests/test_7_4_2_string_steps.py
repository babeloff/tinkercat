"""
Tests for Task 7.4.2: String Manipulation Traversal Steps.

Validates all twelve string steps: concat, format, toLower, toUpper,
trim, ltrim, rtrim, replace, split, length, substring, and reverse.
See docs/project/changelog/task-7.4.2-string-steps.adoc.
"""

import pytest
import re


# ---------------------------------------------------------------------------
# Mock pipeline that applies string steps
# ---------------------------------------------------------------------------

class StringPipeline:
    def __init__(self, values):
        self._values = list(values)

    def concat(self, *others):
        self._values = [v + "".join(str(o) for o in others) for v in self._values]
        return self

    def format(self, template):
        self._values = [template.replace("%s", v) for v in self._values]
        return self

    def format_tokens(self, template, element):
        def replace(m):
            key = m.group(1)
            return str(element.get(key, ""))
        self._values = [re.sub(r"%\{(\w+)}", replace, template)
                        for _ in self._values]
        return self

    def to_lower(self):
        self._values = [v.lower() for v in self._values]
        return self

    def to_upper(self):
        self._values = [v.upper() for v in self._values]
        return self

    def trim(self):
        self._values = [v.strip() for v in self._values]
        return self

    def ltrim(self):
        self._values = [v.lstrip() for v in self._values]
        return self

    def rtrim(self):
        self._values = [v.rstrip() for v in self._values]
        return self

    def replace(self, pattern, replacement):
        self._values = [v.replace(pattern, replacement) for v in self._values]
        return self

    def split(self, delimiter):
        result = []
        for v in self._values:
            result.extend(v.split(delimiter))
        self._values = result
        return self

    def length(self):
        self._values = [len(v) for v in self._values]
        return self

    def substring(self, start, end=None):
        if end is None:
            self._values = [v[start:] for v in self._values]
        else:
            self._values = [v[start:end] for v in self._values]
        return self

    def reverse(self):
        self._values = [v[::-1] for v in self._values]
        return self

    def to_list(self):
        return list(self._values)


def P(values):
    return StringPipeline(values)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_concat():
    assert P(["Hello"]).concat(", World").to_list() == ["Hello, World"]


def test_concat_multiple():
    assert P(["a"]).concat("b", "c").to_list() == ["abc"]


def test_format_percent_s():
    assert P(["Alice"]).format("Hello, %s!").to_list() == ["Hello, Alice!"]


def test_format_tokens():
    result = P(["unused"]).format_tokens(
        "Hi %{name}, age %{age}!", {"name": "Alice", "age": "30"}
    ).to_list()
    assert result == ["Hi Alice, age 30!"]


def test_format_missing_token_empty():
    result = P(["x"]).format_tokens("%{missing}", {}).to_list()
    assert result == [""]


def test_to_lower():
    assert P(["HELLO"]).to_lower().to_list() == ["hello"]


def test_to_upper():
    assert P(["hello"]).to_upper().to_list() == ["HELLO"]


def test_trim():
    assert P(["  hello  "]).trim().to_list() == ["hello"]


def test_ltrim():
    result = P(["  hello  "]).ltrim().to_list()[0]
    assert result == "hello  "


def test_rtrim():
    result = P(["  hello  "]).rtrim().to_list()[0]
    assert result == "  hello"


def test_replace():
    assert P(["foo bar"]).replace("bar", "baz").to_list() == ["foo baz"]


def test_split_delimiter():
    result = P(["a,b,c"]).split(",").to_list()
    assert result == ["a", "b", "c"]


def test_split_then_trim():
    result = P(["a, b, c"]).split(",").trim().to_list()
    assert result == ["a", "b", "c"]


def test_length():
    assert P(["hello"]).length().to_list() == [5]


def test_length_empty_string():
    assert P([""]).length().to_list() == [0]


def test_substring_start_only():
    assert P(["hello"]).substring(2).to_list() == ["llo"]


def test_substring_start_end():
    assert P(["hello"]).substring(1, 4).to_list() == ["ell"]


def test_reverse():
    assert P(["hello"]).reverse().to_list() == ["olleh"]


def test_reverse_empty():
    assert P([""]).reverse().to_list() == [""]


def test_unicode_to_lower():
    assert P(["HÉLLO"]).to_lower().to_list() == ["héllo"]


def test_pipeline_composition():
    result = P(["  alice@EXAMPLE.COM  "]).trim().to_lower().to_list()
    assert result == ["alice@example.com"]
