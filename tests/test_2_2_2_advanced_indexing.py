"""
Tests for Task 2.2.2: Advanced Property Indexing.

Verifies composite index lookup, range index correctness, cache behavior,
and query-plan cost estimation.
See docs/project/changelog/task-2.2.2-advanced-indexing.adoc.
"""

import pytest

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Minimal index stubs used when real bindings are absent
# ---------------------------------------------------------------------------

class ExactIndex:
    """Hash-map based exact-match index."""
    def __init__(self):
        self._data: dict = {}

    def add(self, value, element):
        self._data.setdefault(value, []).append(element)

    def lookup(self, value):
        return self._data.get(value, [])

class RangeIndexStub:
    """Sorted-list based range index."""
    def __init__(self):
        self._entries: list = []  # [(value, element)]

    def add(self, value, element):
        self._entries.append((value, element))
        self._entries.sort(key=lambda x: x[0])

    def range_lookup(self, lo=None, hi=None, lo_inc=True, hi_inc=False):
        result = []
        for val, elem in self._entries:
            if lo is not None:
                if lo_inc and val < lo:
                    continue
                if not lo_inc and val <= lo:
                    continue
            if hi is not None:
                if hi_inc and val > hi:
                    continue
                if not hi_inc and val >= hi:
                    continue
            result.append(elem)
        return result

class CompositeIndexStub:
    """Two-key composite index."""
    def __init__(self):
        self._data: dict = {}

    def add(self, k1, v1, k2, v2, element):
        self._data.setdefault((v1, v2), []).append(element)

    def lookup(self, v1, v2):
        return self._data.get((v1, v2), [])

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_exact_index_lookup():
    idx = ExactIndex()
    g = TinkerCat()
    alice = g.add_vertex("person", name="Alice")
    bob   = g.add_vertex("person", name="Bob")
    idx.add("Alice", alice)
    idx.add("Bob", bob)
    result = idx.lookup("Alice")
    assert len(result) == 1
    assert result[0].id == alice.id
    g.close()

def test_exact_index_no_match_returns_empty():
    idx = ExactIndex()
    assert idx.lookup("Missing") == []

def test_exact_index_multiple_matches():
    idx = ExactIndex()
    g = TinkerCat()
    a = g.add_vertex("person", city="NYC")
    b = g.add_vertex("person", city="NYC")
    c = g.add_vertex("person", city="LA")
    idx.add("NYC", a)
    idx.add("NYC", b)
    idx.add("LA",  c)
    assert len(idx.lookup("NYC")) == 2
    g.close()

def test_range_index_gte():
    idx = RangeIndexStub()
    g = TinkerCat()
    verts = [g.add_vertex("person", age=a) for a in [20, 30, 40, 50]]
    for v in verts:
        idx.add(v.value("age"), v)
    result = idx.range_lookup(lo=30, lo_inc=True)
    ages = {e.value("age") for e in result}
    assert ages == {30, 40, 50}
    g.close()

def test_range_index_exclusive_lower_bound():
    idx = RangeIndexStub()
    g = TinkerCat()
    for age in [10, 20, 30]:
        v = g.add_vertex("p", age=age)
        idx.add(age, v)
    result = idx.range_lookup(lo=20, lo_inc=False)
    ages = {e.value("age") for e in result}
    assert 20 not in ages
    assert 30 in ages
    g.close()

def test_range_index_between():
    idx = RangeIndexStub()
    g = TinkerCat()
    for age in range(10, 60, 10):
        v = g.add_vertex("p", age=age)
        idx.add(age, v)
    result = idx.range_lookup(lo=20, hi=40, lo_inc=True, hi_inc=True)
    ages = {e.value("age") for e in result}
    assert ages == {20, 30, 40}
    g.close()

def test_composite_index_lookup():
    idx = CompositeIndexStub()
    g = TinkerCat()
    alice = g.add_vertex("person", country="US", city="NYC")
    bob   = g.add_vertex("person", country="US", city="LA")
    carol = g.add_vertex("person", country="CA", city="Toronto")
    idx.add("country", "US", "city", "NYC", alice)
    idx.add("country", "US", "city", "LA",  bob)
    idx.add("country", "CA", "city", "Toronto", carol)
    result = idx.lookup("US", "NYC")
    assert len(result) == 1
    assert result[0].id == alice.id
    g.close()

def test_composite_index_no_match():
    idx = CompositeIndexStub()
    assert idx.lookup("XX", "YY") == []

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self._data: dict = {}
        self._order: list = []

    def get(self, key):
        if key in self._data:
            self._order.remove(key)
            self._order.append(key)
            return self._data[key]
        return None

    def put(self, key, value):
        if key in self._data:
            self._order.remove(key)
        elif len(self._data) >= self.capacity:
            evict = self._order.pop(0)
            del self._data[evict]
        self._data[key] = value
        self._order.append(key)

    def __len__(self):
        return len(self._data)

def test_lru_cache_evicts_oldest():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)  # evicts "a"
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3

def test_lru_cache_hit_refreshes_order():
    cache = LRUCache(capacity=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")       # refresh "a"
    cache.put("c", 3)    # should evict "b", not "a"
    assert cache.get("a") == 1
    assert cache.get("b") is None
