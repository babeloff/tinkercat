"""
Predicate class mirroring TinkerPop's P.

Used by filter steps such as all() and any() to express conditions on
traversal elements.  Mirrors the Kotlin P class (task 7.7.2 / 7.8.2).
"""

from __future__ import annotations
from typing import Any, Callable


class P:
    """A composable predicate for use in traversal filter steps."""

    def __init__(self, test_fn: Callable[[Any], bool], value: Any = None):
        self._test_fn = test_fn
        self.value = value

    def test(self, v: Any) -> bool:
        return self._test_fn(v)

    def negate(self) -> "P":
        return P(lambda v: not self._test_fn(v))

    def and_(self, other: "P") -> "P":
        return P(lambda v: self._test_fn(v) and other.test(v))

    def or_(self, other: "P") -> "P":
        return P(lambda v: self._test_fn(v) or other.test(v))

    # ── Factory methods ───────────────────────────────────────────────────────

    @staticmethod
    def eq(value: Any) -> "P":
        return P(lambda v: v == value, value)

    @staticmethod
    def neq(value: Any) -> "P":
        return P(lambda v: v != value, value)

    @staticmethod
    def gt(value: Any) -> "P":
        return P(lambda v: v is not None and v > value, value)

    @staticmethod
    def gte(value: Any) -> "P":
        return P(lambda v: v is not None and v >= value, value)

    @staticmethod
    def lt(value: Any) -> "P":
        return P(lambda v: v is not None and v < value, value)

    @staticmethod
    def lte(value: Any) -> "P":
        return P(lambda v: v is not None and v <= value, value)

    @staticmethod
    def between(min_val: Any, max_val: Any) -> "P":
        return P(lambda v: v is not None and min_val <= v < max_val)

    @staticmethod
    def within(*values: Any) -> "P":
        vals = set(values)
        return P(lambda v: v in vals, values)

    @staticmethod
    def without(*values: Any) -> "P":
        vals = set(values)
        return P(lambda v: v not in vals, values)

    @staticmethod
    def starting_with(prefix: str) -> "P":
        return P(lambda v: isinstance(v, str) and v.startswith(prefix), prefix)

    @staticmethod
    def not_starting_with(prefix: str) -> "P":
        return P(lambda v: isinstance(v, str) and not v.startswith(prefix), prefix)

    @staticmethod
    def ending_with(suffix: str) -> "P":
        return P(lambda v: isinstance(v, str) and v.endswith(suffix), suffix)

    @staticmethod
    def not_ending_with(suffix: str) -> "P":
        return P(lambda v: isinstance(v, str) and not v.endswith(suffix), suffix)

    @staticmethod
    def containing(substring: str) -> "P":
        return P(lambda v: isinstance(v, str) and substring in v, substring)

    @staticmethod
    def not_containing(substring: str) -> "P":
        return P(lambda v: isinstance(v, str) and substring not in v, substring)

    @staticmethod
    def regexp(pattern: str) -> "P":
        import re
        compiled = re.compile(pattern)
        return P(lambda v: isinstance(v, str) and bool(compiled.search(v)), pattern)
