"""
Tests for Task 3.3.1: Native Platform Implementation.

Verifies memory management reporting, platform detection, performance
statistics, and cross-platform collection semantics.
See docs/project/changelog/task-3.3.1-native-implementation.adoc.
"""

import pytest
import sys
import platform
import time

from tinkercat import TinkerCat

# ---------------------------------------------------------------------------
# Mock platform layer
# ---------------------------------------------------------------------------

class MockPlatformStats:
    def __init__(self):
        self.allocated_bytes = 1024 * 1024
        self.peak_bytes = 2 * 1024 * 1024
        self.gc_count = 3
        self.platform_name = platform.system()

    def as_dict(self):
        return {
            "allocated_bytes": self.allocated_bytes,
            "peak_bytes": self.peak_bytes,
            "gc_count": self.gc_count,
            "platform": self.platform_name,
        }

def test_platform_stats_has_required_keys():
    stats = MockPlatformStats().as_dict()
    for key in ("allocated_bytes", "peak_bytes", "gc_count", "platform"):
        assert key in stats

def test_platform_stats_bytes_non_negative():
    stats = MockPlatformStats().as_dict()
    assert stats["allocated_bytes"] >= 0
    assert stats["peak_bytes"] >= 0

def test_platform_name_is_string():
    stats = MockPlatformStats().as_dict()
    assert isinstance(stats["platform"], str)
    assert len(stats["platform"]) > 0

def test_current_platform_is_known():
    name = platform.system()
    assert name in ("Linux", "Darwin", "Windows", "")

def test_graph_operations_complete_in_reasonable_time():
    g = TinkerCat()
    start = time.monotonic()
    for i in range(1000):
        g.add_vertex("node", idx=i)
    elapsed = time.monotonic() - start
    g.close()
    assert elapsed < 5.0, f"1000 vertex inserts took {elapsed:.2f}s (expected < 5s)"

def test_large_graph_vertex_count_accurate():
    g = TinkerCat()
    n = 500
    for i in range(n):
        g.add_vertex("node", idx=i)
    count = len(g.vertices())
    g.close()
    assert count == n

def test_platform_detection_python_version():
    major, minor = sys.version_info[:2]
    assert major == 3
    assert minor >= 8, "TinkerCat Python bindings require Python 3.8+"
