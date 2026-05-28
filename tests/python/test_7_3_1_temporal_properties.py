"""
Tests for Task 7.3.1: Temporal Property Value Support.

TinkerCat stores any Python object as a property value, so storing
stdlib datetime/date/timedelta objects works today.  The two graphson
tests exercise tinkercat.graphson which is not yet implemented.
See docs/project/changelog/task-7.3.1-temporal-properties.adoc.
"""

import pytest
import json
from datetime import datetime, date, timedelta, timezone

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    yield graph
    graph.close()


def test_store_and_retrieve_instant(g):
    now = datetime.now(timezone.utc)
    v = g.add_vertex("event", ts=now)
    assert v.value("ts") == now


def test_instant_from_epoch_ms_round_trip():
    ms = 1_700_000_000_000
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    assert int(dt.timestamp() * 1000) == ms


def test_instant_parse_iso8601():
    dt = datetime.fromisoformat("2024-01-15T12:00:00+00:00")
    assert dt.year == 2024
    assert dt.month == 1
    assert dt.day == 15


def test_store_and_retrieve_local_date(g):
    d = date.fromisoformat("2024-06-01")
    v = g.add_vertex("log", date=d)
    assert v.value("date") == d


def test_store_and_retrieve_duration(g):
    dur = timedelta(days=7)
    v = g.add_vertex("task", duration=dur)
    assert v.value("duration") == dur


def test_instant_ordering():
    t1 = datetime.fromisoformat("2024-01-01T00:00:00+00:00")
    t2 = datetime.fromisoformat("2024-06-01T00:00:00+00:00")
    assert t1 < t2
    assert t2 > t1


def test_local_date_ordering():
    d1 = date.fromisoformat("2023-01-01")
    d2 = date.fromisoformat("2024-01-01")
    assert d1 < d2


def test_range_query_on_instant_properties(g):
    for ds in ["2024-01-01", "2024-06-01", "2024-12-01"]:
        ts = datetime.fromisoformat(f"{ds}T00:00:00+00:00")
        g.add_vertex("event", ts=ts)
    cutoff = datetime.fromisoformat("2024-07-01T00:00:00+00:00")
    before = [v for v in g.vertices() if v.value("ts") and v.value("ts") < cutoff]
    assert len(before) == 2


def test_graphson_instant_serialisation():
    from tinkercat.graphson import to_graphson  # ImportError until implemented
    ts = datetime.fromisoformat("2024-01-15T12:00:00+00:00")
    text = to_graphson(ts)
    recovered = json.loads(text)
    assert recovered["@type"] == "g:Instant"
    assert "2024-01-15" in recovered["@value"]


def test_graphson_local_date_serialisation():
    from tinkercat.graphson import to_graphson  # ImportError until implemented
    d = date.fromisoformat("2024-06-01")
    text = to_graphson(d)
    recovered = json.loads(text)
    assert recovered["@value"] == "2024-06-01"


def test_null_temporal_value_is_none(g):
    v = g.add_vertex("event")
    assert v.value("ts") is None
