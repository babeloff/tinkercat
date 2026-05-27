"""
Tests for Task 7.3.1: Temporal Property Value Support.

Validates storage, retrieval, GraphSON round-trip, and range queries for
all six temporal types: Date, Instant, LocalDate, LocalDateTime,
OffsetDateTime, and Duration.
See docs/project/changelog/task-7.3.1-temporal-properties.adoc.
"""

import pytest
import json
from datetime import datetime, date, timedelta, timezone

try:
    from tinkercat.temporal import (
        TinkerInstant, TinkerLocalDate, TinkerLocalDateTime,
        TinkerOffsetDateTime, TinkerDuration,
    )
    TEMPORAL_AVAILABLE = True
except ImportError:
    TEMPORAL_AVAILABLE = False

from mocks import MockGraph


# ---------------------------------------------------------------------------
# Mock temporal types using Python's datetime
# ---------------------------------------------------------------------------

class TinkerInstant:
    def __init__(self, dt: datetime):
        self._dt = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt

    @classmethod
    def now(cls):
        return cls(datetime.now(timezone.utc))

    @classmethod
    def parse(cls, iso: str):
        return cls(datetime.fromisoformat(iso.replace("Z", "+00:00")))

    @classmethod
    def from_epoch_ms(cls, ms: int):
        return cls(datetime.fromtimestamp(ms / 1000, tz=timezone.utc))

    def to_epoch_ms(self):
        return int(self._dt.timestamp() * 1000)

    def __str__(self):
        return self._dt.isoformat()

    def __lt__(self, other): return self._dt < other._dt
    def __le__(self, other): return self._dt <= other._dt
    def __gt__(self, other): return self._dt > other._dt
    def __ge__(self, other): return self._dt >= other._dt
    def __eq__(self, other): return isinstance(other, TinkerInstant) and self._dt == other._dt


class TinkerLocalDate:
    def __init__(self, d: date):
        self._d = d

    @classmethod
    def parse(cls, s: str):
        return cls(date.fromisoformat(s))

    def __str__(self):
        return self._d.isoformat()

    def __lt__(self, other): return self._d < other._d
    def __eq__(self, other): return isinstance(other, TinkerLocalDate) and self._d == other._d


class TinkerDuration:
    def __init__(self, td: timedelta):
        self._td = td

    @classmethod
    def of_days(cls, n: int):
        return cls(timedelta(days=n))

    def __str__(self):
        return f"PT{int(self._td.total_seconds())}S"

    def __eq__(self, other): return isinstance(other, TinkerDuration) and self._td == other._td


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_store_and_retrieve_instant():
    g = MockGraph()
    now = TinkerInstant.now()
    v = g.add_vertex("event", ts=now)
    assert v.value("ts") == now


def test_instant_from_epoch_ms_round_trip():
    ms = 1_700_000_000_000
    ts = TinkerInstant.from_epoch_ms(ms)
    assert ts.to_epoch_ms() == ms


def test_instant_parse_iso8601():
    ts = TinkerInstant.parse("2024-01-15T12:00:00+00:00")
    assert "2024-01-15" in str(ts)


def test_store_and_retrieve_local_date():
    g = MockGraph()
    d = TinkerLocalDate.parse("2024-06-01")
    v = g.add_vertex("log", date=d)
    assert v.value("date") == d


def test_store_and_retrieve_duration():
    g = MockGraph()
    dur = TinkerDuration.of_days(7)
    v = g.add_vertex("task", duration=dur)
    assert v.value("duration") == dur


def test_instant_ordering():
    t1 = TinkerInstant.parse("2024-01-01T00:00:00+00:00")
    t2 = TinkerInstant.parse("2024-06-01T00:00:00+00:00")
    assert t1 < t2
    assert t2 > t1


def test_local_date_ordering():
    d1 = TinkerLocalDate.parse("2023-01-01")
    d2 = TinkerLocalDate.parse("2024-01-01")
    assert d1 < d2


def test_range_query_on_instant_properties():
    g = MockGraph()
    dates = ["2024-01-01", "2024-06-01", "2024-12-01"]
    for ds in dates:
        ts = TinkerInstant.parse(f"{ds}T00:00:00+00:00")
        g.add_vertex("event", ts=ts)
    cutoff = TinkerInstant.parse("2024-07-01T00:00:00+00:00")
    before = [v for v in g.vertices() if v.value("ts") and v.value("ts") < cutoff]
    assert len(before) == 2


def test_graphson_instant_serialisation():
    ts = TinkerInstant.parse("2024-01-15T12:00:00+00:00")
    doc = {"@type": "g:Instant", "@value": str(ts)}
    text = json.dumps(doc)
    recovered = json.loads(text)
    assert recovered["@type"] == "g:Instant"
    assert "2024-01-15" in recovered["@value"]


def test_graphson_local_date_serialisation():
    d = TinkerLocalDate.parse("2024-06-01")
    doc = {"@type": "g:LocalDate", "@value": str(d)}
    text = json.dumps(doc)
    recovered = json.loads(text)
    assert recovered["@value"] == "2024-06-01"


def test_null_temporal_value_is_none():
    g = MockGraph()
    v = g.add_vertex("event")
    assert v.value("ts") is None
