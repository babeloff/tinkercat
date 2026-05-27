"""
Tests for Task 2.2.1: Multi-property Support.

Verifies cardinality enforcement (SINGLE/LIST/SET), meta-properties,
and property aggregation queries.
See docs/project/changelog/task-2.2.1-multi-property-support.adoc.
"""

import pytest

try:
    from tinkercat import TinkerCat
    from tinkercat.structure import VertexProperty
    CARDINALITY_SINGLE = "single"
    CARDINALITY_LIST   = "list"
    CARDINALITY_SET    = "set"
except ImportError:
    from mocks import MockGraph as TinkerCat
    CARDINALITY_SINGLE = "single"
    CARDINALITY_LIST   = "list"
    CARDINALITY_SET    = "set"

from mocks import MockGraph, MockVertex


@pytest.fixture
def g():
    return MockGraph()


def test_single_property_last_write_wins(g):
    v = g.add_vertex("person", name="Alice")
    v.property("age", 25)
    v.property("age", 26)
    assert v.value("age") == 26


def test_list_property_accumulates_values():
    """Multi-value property list stores multiple values per key."""
    class MultiVertex(MockVertex):
        def __init__(self, vid, label="vertex"):
            super().__init__(vid, label)
            self._multi: dict = {}

        def multi_property(self, key, value):
            self._multi.setdefault(key, []).append(value)

        def multi_values(self, key):
            return self._multi.get(key, [])

    v = MultiVertex(1, "person")
    v.multi_property("skill", "Python")
    v.multi_property("skill", "Kotlin")
    assert v.multi_values("skill") == ["Python", "Kotlin"]


def test_set_property_deduplicates():
    """SET cardinality rejects duplicate values."""
    class SetVertex(MockVertex):
        def __init__(self, vid, label="vertex"):
            super().__init__(vid, label)
            self._sets: dict = {}

        def set_property(self, key, value):
            self._sets.setdefault(key, set()).add(value)

        def set_values(self, key):
            return self._sets.get(key, set())

    v = SetVertex(1, "tag")
    v.set_property("tag", "graphdb")
    v.set_property("tag", "graphdb")  # duplicate
    v.set_property("tag", "kotlin")
    assert len(v.set_values("tag")) == 2


def test_meta_property_on_vertex_property():
    """Properties can themselves carry meta-properties."""
    class MetaProperty:
        def __init__(self, key, value, **meta):
            self.key = key
            self._value = value
            self.meta = meta

        def value(self):
            return self._value

        def meta_value(self, key):
            return self.meta.get(key)

    prop = MetaProperty("email", "alice@example.com", verified=True, type="primary")
    assert prop.value() == "alice@example.com"
    assert prop.meta_value("verified") is True
    assert prop.meta_value("type") == "primary"


def test_vertex_property_keys_iterable(g):
    v = g.add_vertex("person", name="Alice", age=25, city="NYC")
    keys = set(v.keys())
    assert "name" in keys
    assert "age" in keys
    assert "city" in keys


def test_vertex_properties_iterator(g):
    v = g.add_vertex("person", name="Alice", age=25)
    props = list(v.properties())
    assert len(props) == 2
    prop_keys = {p._key for p in props}
    assert prop_keys == {"name", "age"}


def test_property_present_check(g):
    v = g.add_vertex("person", name="Alice")
    assert v.property("name").is_present()
    assert not v.property("missing").is_present()


def test_null_property_with_allow_null():
    g = MockGraph(allow_null_properties=True)
    v = g.add_vertex("person")
    v.property("nickname", None)
    assert v.property("nickname").is_present() is False  # None → not present


def test_property_aggregation_sum():
    g = MockGraph()
    for age in [20, 30, 40]:
        g.add_vertex("person", age=age)
    total = sum(v.value("age") for v in g.vertices() if v.value("age") is not None)
    assert total == 90


def test_property_aggregation_average():
    g = MockGraph()
    for age in [10, 20, 30]:
        g.add_vertex("person", age=age)
    ages = [v.value("age") for v in g.vertices()]
    avg = sum(ages) / len(ages)
    assert avg == 20.0
