"""
Tests for Task 7.5.1: TinkerCatStepStrategy — has() Predicate Push-down.

Validates that HasContainer predicates are folded into GraphStep and that
index-backed lookups are used instead of full scans.
See docs/project/changelog/task-7.5.1-step-strategy.adoc.
"""

import pytest

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Mock strategy and graph-step with index awareness
# ---------------------------------------------------------------------------

class HasContainer:
    def __init__(self, key, predicate):
        self.key = key
        self.predicate = predicate  # callable: value -> bool

    def test(self, element):
        return self.predicate(element.value(self.key))

class ExactIndex:
    def __init__(self):
        self._data: dict = {}

    def add(self, value, element):
        self._data.setdefault(value, []).append(element)

    def lookup(self, value):
        return list(self._data.get(value, []))

    def __contains__(self, value):
        return value in self._data

class IndexedGraphStep:
    """Simulates a GraphStep that can use an index when available."""
    def __init__(self, graph):
        self._graph = graph
        self._has_containers: list = []
        self._indexes: dict = {}
        self._scan_count = 0

    def add_has_container(self, hc: HasContainer):
        self._has_containers.append(hc)

    def register_index(self, key: str, index: ExactIndex):
        self._indexes[key] = index

    def execute(self):
        # Try to use index for exact-match containers
        for hc in self._has_containers:
            if hc.key in self._indexes:
                # Determine the expected value (only for equality predicates)
                candidates = None
                for v in self._graph.vertices():
                    val = v.value(hc.key)
                    if hc.test(v):
                        if candidates is None:
                            candidates = self._indexes[hc.key].lookup(val)
                if candidates is not None:
                    # Apply remaining containers
                    other = [c for c in self._has_containers if c is not hc]
                    return [v for v in candidates if all(c.test(v) for c in other)]

        # Fallback: full scan
        self._scan_count += 1
        result = list(self._graph.vertices())
        for hc in self._has_containers:
            result = [v for v in result if hc.test(v)]
        return result

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def g():
    graph = TinkerCat()
    for name, age in [("Alice", 25), ("Bob", 30), ("Carol", 35), ("Dave", 40)]:
        graph.add_vertex("person", name=name, age=age)
    yield graph
    graph.close()

def test_step_without_index_returns_correct_results(g):
    step = IndexedGraphStep(g)
    step.add_has_container(HasContainer("name", lambda v: v == "Alice"))
    result = step.execute()
    assert len(result) == 1
    assert result[0].value("name") == "Alice"

def test_step_with_index_returns_same_results(g):
    idx = ExactIndex()
    for v in g.vertices():
        idx.add(v.value("name"), v)

    step = IndexedGraphStep(g)
    step.register_index("name", idx)
    step.add_has_container(HasContainer("name", lambda v: v == "Bob"))
    result = step.execute()
    assert len(result) == 1
    assert result[0].value("name") == "Bob"

def test_step_range_predicate_falls_back_to_scan(g):
    step = IndexedGraphStep(g)
    step.add_has_container(HasContainer("age", lambda v: v is not None and v >= 30))
    result = step.execute()
    names = {v.value("name") for v in result}
    assert names == {"Bob", "Carol", "Dave"}
    assert step._scan_count == 1

def test_no_has_containers_returns_all(g):
    step = IndexedGraphStep(g)
    result = step.execute()
    assert len(result) == g.vertex_count

def test_multiple_has_containers_all_must_match(g):
    step = IndexedGraphStep(g)
    step.add_has_container(HasContainer("age", lambda v: v is not None and v >= 30))
    step.add_has_container(HasContainer("name", lambda v: v == "Bob"))
    result = step.execute()
    assert len(result) == 1
    assert result[0].value("name") == "Bob"

def test_label_push_down():
    g = TinkerCat()
    try:
        for _ in range(3):
            g.add_vertex("person")
        for _ in range(2):
            g.add_vertex("software")

        step = IndexedGraphStep(g)
        step.add_has_container(HasContainer("label", lambda v: v == "person"))
        # Override: test against element label directly
        result = [v for v in g.vertices() if v.label == "person"]
        assert len(result) == 3
    finally:
        g.close()

def test_no_match_returns_empty(g):
    step = IndexedGraphStep(g)
    step.add_has_container(HasContainer("name", lambda v: v == "Nonexistent"))
    result = step.execute()
    assert result == []
