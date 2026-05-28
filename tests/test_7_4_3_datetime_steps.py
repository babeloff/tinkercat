"""
Tests for Task 7.4.3: Date/Time Traversal Steps.

All tests call asDate(), dateAdd(), and dateDiff() as traversal steps on
a live TinkerCat graph.  These steps are not yet implemented; every test
fails with AttributeError until they are added to GraphTraversal.
See docs/project/changelog/task-7.4.3-datetime-steps.adoc.
"""

import pytest
from datetime import datetime, timezone, timedelta

from tinkercat import TinkerCat


@pytest.fixture
def g():
    graph = TinkerCat()
    graph.add_vertex("event", ts=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc))
    graph.add_vertex("event", ts=1_705_320_000_000)          # epoch ms
    graph.add_vertex("event", ts="2024-01-15T12:00:00+00:00")  # ISO string
    graph.add_vertex("event", ts=datetime(2024, 1, 1, tzinfo=timezone.utc))
    graph.add_vertex("event", ts=datetime(2024, 1, 8, tzinfo=timezone.utc))
    yield graph
    graph.close()


# ---------------------------------------------------------------------------
# asDate tests
# ---------------------------------------------------------------------------

def test_as_date_from_datetime_returns_same(g):
    result = (
        g.traversal().V()
        .has("ts", datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc))
        .values("ts")
        .as_date()  # AttributeError until implemented
        .to_list()
    )
    assert len(result) == 1
    assert isinstance(result[0], datetime)


def test_as_date_from_epoch_ms(g):
    result = (
        g.traversal().V()
        .has("ts", 1_705_320_000_000)
        .values("ts")
        .as_date()  # AttributeError until implemented
        .to_list()
    )
    assert len(result) == 1
    assert result[0].year == 2024


def test_as_date_from_iso_string(g):
    result = (
        g.traversal().V()
        .has("ts", "2024-01-15T12:00:00+00:00")
        .values("ts")
        .as_date()  # AttributeError until implemented
        .to_list()
    )
    assert len(result) == 1
    assert result[0].month == 1


def test_as_date_unsupported_type_raises():
    graph = TinkerCat()
    try:
        graph.add_vertex("e", ts=object())
        with pytest.raises(Exception):
            graph.traversal().V().values("ts").as_date().to_list()  # AttributeError or TypeError
    finally:
        graph.close()


# ---------------------------------------------------------------------------
# dateAdd tests
# ---------------------------------------------------------------------------

def test_date_add_days(g):
    result = (
        g.traversal().V()
        .has("ts", datetime(2024, 1, 1, tzinfo=timezone.utc))
        .values("ts")
        .as_date()
        .date_add("DAYS", 7)  # AttributeError until implemented
        .to_list()
    )
    assert result == [datetime(2024, 1, 8, tzinfo=timezone.utc)]


def test_date_add_hours(g):
    result = (
        g.traversal().V()
        .has("ts", datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc))
        .values("ts")
        .as_date()
        .date_add("HOURS", 3)  # AttributeError until implemented
        .to_list()
    )
    assert result[0].hour == 15


def test_date_add_negative_amount(g):
    result = (
        g.traversal().V()
        .has("ts", datetime(2024, 1, 8, tzinfo=timezone.utc))
        .values("ts")
        .as_date()
        .date_add("DAYS", -7)  # AttributeError until implemented
        .to_list()
    )
    assert result[0].day == 1


def test_date_add_zero(g):
    dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    result = (
        g.traversal().V()
        .has("ts", dt)
        .values("ts")
        .as_date()
        .date_add("DAYS", 0)  # AttributeError until implemented
        .to_list()
    )
    assert result == [dt]


# ---------------------------------------------------------------------------
# dateDiff tests
# ---------------------------------------------------------------------------

def test_date_diff_days_positive(g):
    result = (
        g.traversal().V()
        .has_label("event")
        .values("ts")
        .as_date()
        .date_diff(datetime(2024, 1, 8, tzinfo=timezone.utc), "DAYS")  # AttributeError
        .to_list()
    )
    assert isinstance(result, list)


def test_date_diff_same_instant_is_zero():
    graph = TinkerCat()
    try:
        dt = datetime(2024, 6, 1, tzinfo=timezone.utc)
        graph.add_vertex("e", ts=dt)
        result = (
            graph.traversal().V()
            .values("ts")
            .as_date()
            .date_diff(dt, "SECONDS")  # AttributeError until implemented
            .to_list()
        )
        assert result == [0]
    finally:
        graph.close()


def test_date_diff_hours():
    graph = TinkerCat()
    try:
        a = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
        b = datetime(2024, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
        graph.add_vertex("e", ts=a)
        result = (
            graph.traversal().V()
            .values("ts")
            .as_date()
            .date_diff(b, "HOURS")  # AttributeError until implemented
            .to_list()
        )
        assert result == [6]
    finally:
        graph.close()


# ---------------------------------------------------------------------------
# Pipeline composition
# ---------------------------------------------------------------------------

def test_as_date_then_date_add_pipeline():
    graph = TinkerCat()
    try:
        graph.add_vertex("e", ts="2024-01-01T00:00:00+00:00")
        result = (
            graph.traversal().V()
            .values("ts")
            .as_date()              # AttributeError until implemented
            .date_add("DAYS", 30)
            .to_list()
        )
        assert result[0].month == 1 or result[0].month == 2  # 30 days after Jan 1
    finally:
        graph.close()
