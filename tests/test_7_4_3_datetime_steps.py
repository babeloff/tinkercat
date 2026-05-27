"""
Tests for Task 7.4.3: Date/Time Traversal Steps.

Validates asDate(), dateAdd(), and dateDiff() step semantics using
Python datetime objects as mock temporal values.
See docs/project/changelog/task-7.4.3-datetime-steps.adoc.
"""

import pytest
from datetime import datetime, timezone, timedelta
from enum import Enum


class DurationUnit(Enum):
    MILLISECONDS = "ms"
    SECONDS      = "s"
    MINUTES      = "min"
    HOURS        = "h"
    DAYS         = "d"


# ---------------------------------------------------------------------------
# Mock step implementations
# ---------------------------------------------------------------------------

def as_date(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    if isinstance(value, str):
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    raise TypeError(f"Cannot convert {type(value).__name__} to datetime")


_UNIT_DELTA = {
    DurationUnit.MILLISECONDS: lambda n: timedelta(milliseconds=n),
    DurationUnit.SECONDS:      lambda n: timedelta(seconds=n),
    DurationUnit.MINUTES:      lambda n: timedelta(minutes=n),
    DurationUnit.HOURS:        lambda n: timedelta(hours=n),
    DurationUnit.DAYS:         lambda n: timedelta(days=n),
}


def date_add(dt, unit: DurationUnit, amount: int):
    return dt + _UNIT_DELTA[unit](amount)


def date_diff(dt_a, dt_b, unit: DurationUnit):
    delta = dt_b - dt_a
    total_s = delta.total_seconds()
    divisors = {
        DurationUnit.MILLISECONDS: 0.001,
        DurationUnit.SECONDS:      1,
        DurationUnit.MINUTES:      60,
        DurationUnit.HOURS:        3600,
        DurationUnit.DAYS:         86400,
    }
    return int(total_s / divisors[unit])


# ---------------------------------------------------------------------------
# asDate tests
# ---------------------------------------------------------------------------

def test_as_date_from_datetime_returns_same():
    dt = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    result = as_date(dt)
    assert result == dt


def test_as_date_from_epoch_ms():
    ms = 1_705_320_000_000  # 2024-01-15 12:00:00 UTC
    result = as_date(ms)
    assert isinstance(result, datetime)
    assert result.year == 2024


def test_as_date_from_iso_string():
    result = as_date("2024-01-15T12:00:00+00:00")
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 15


def test_as_date_unsupported_type_raises():
    with pytest.raises(TypeError):
        as_date(object())


# ---------------------------------------------------------------------------
# dateAdd tests
# ---------------------------------------------------------------------------

def test_date_add_days():
    dt = datetime(2024, 1, 1, tzinfo=timezone.utc)
    result = date_add(dt, DurationUnit.DAYS, 7)
    assert result == datetime(2024, 1, 8, tzinfo=timezone.utc)


def test_date_add_hours():
    dt = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    result = date_add(dt, DurationUnit.HOURS, 3)
    assert result.hour == 13


def test_date_add_negative_amount():
    dt = datetime(2024, 1, 8, tzinfo=timezone.utc)
    result = date_add(dt, DurationUnit.DAYS, -7)
    assert result.day == 1


def test_date_add_zero():
    dt = datetime(2024, 6, 1, tzinfo=timezone.utc)
    result = date_add(dt, DurationUnit.DAYS, 0)
    assert result == dt


# ---------------------------------------------------------------------------
# dateDiff tests
# ---------------------------------------------------------------------------

def test_date_diff_days_positive():
    a = datetime(2024, 1, 1, tzinfo=timezone.utc)
    b = datetime(2024, 1, 8, tzinfo=timezone.utc)
    assert date_diff(a, b, DurationUnit.DAYS) == 7


def test_date_diff_days_negative():
    a = datetime(2024, 1, 8, tzinfo=timezone.utc)
    b = datetime(2024, 1, 1, tzinfo=timezone.utc)
    assert date_diff(a, b, DurationUnit.DAYS) == -7


def test_date_diff_same_instant_is_zero():
    dt = datetime(2024, 6, 1, tzinfo=timezone.utc)
    assert date_diff(dt, dt, DurationUnit.SECONDS) == 0


def test_date_diff_hours():
    a = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
    b = datetime(2024, 1, 1, 15, 0, 0, tzinfo=timezone.utc)
    assert date_diff(a, b, DurationUnit.HOURS) == 6


# ---------------------------------------------------------------------------
# Pipeline composition
# ---------------------------------------------------------------------------

def test_as_date_then_date_add_pipeline():
    raw = "2024-01-01T00:00:00+00:00"
    dt  = as_date(raw)
    shifted = date_add(dt, DurationUnit.DAYS, 30)
    diff = date_diff(dt, shifted, DurationUnit.DAYS)
    assert diff == 30
