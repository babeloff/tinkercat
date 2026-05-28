"""
Tests for Task 7.6.1: GraphBinary 4.0 Serialisation.

All tests import write_graph / read_graph / write_value / read_value
from tinkercat.graphbinary.  That module does not yet exist; every test
fails with ImportError until the GraphBinary codec is implemented.
See docs/project/changelog/task-7.6.1-graphbinary.adoc.
"""

import pytest
import io

from tinkercat import TinkerCat
from mocks import build_modern_graph


def test_round_trip_vertex_count():
    from tinkercat.graphbinary import write_graph, read_graph  # ImportError until implemented
    g1 = TinkerCat()
    build_modern_graph(g1)
    data = write_graph(g1)
    g2 = read_graph(data)
    assert g2.vertex_count == g1.vertex_count
    g1.close()
    g2.close()


def test_round_trip_edge_count():
    from tinkercat.graphbinary import write_graph, read_graph  # ImportError until implemented
    g1 = TinkerCat()
    build_modern_graph(g1)
    data = write_graph(g1)
    g2 = read_graph(data)
    assert g2.edge_count == g1.edge_count
    g1.close()
    g2.close()


def test_round_trip_string_property():
    from tinkercat.graphbinary import write_graph, read_graph  # ImportError until implemented
    g1 = TinkerCat()
    g1.add_vertex("person", name="Alice")
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert v.value("name") == "Alice"
    g1.close()
    g2.close()


def test_round_trip_int_property():
    from tinkercat.graphbinary import write_graph, read_graph  # ImportError until implemented
    g1 = TinkerCat()
    g1.add_vertex("person", age=30)
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert v.value("age") == 30
    g1.close()
    g2.close()


def test_round_trip_float_property():
    from tinkercat.graphbinary import write_graph, read_graph  # ImportError until implemented
    g1 = TinkerCat()
    g1.add_vertex("item", score=3.14)
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert abs(v.value("score") - 3.14) < 1e-9
    g1.close()
    g2.close()


def test_round_trip_bool_property():
    from tinkercat.graphbinary import write_graph, read_graph  # ImportError until implemented
    g1 = TinkerCat()
    g1.add_vertex("item", active=True)
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert v.value("active") is True
    g1.close()
    g2.close()


def test_write_value_int():
    from tinkercat.graphbinary import write_value, read_value  # ImportError until implemented
    buf = io.BytesIO()
    write_value(buf, 42)
    buf.seek(0)
    assert read_value(buf) == 42


def test_write_value_string():
    from tinkercat.graphbinary import write_value, read_value  # ImportError until implemented
    buf = io.BytesIO()
    write_value(buf, "hello")
    buf.seek(0)
    assert read_value(buf) == "hello"


def test_write_value_bool_true():
    from tinkercat.graphbinary import write_value, read_value  # ImportError until implemented
    buf = io.BytesIO()
    write_value(buf, True)
    buf.seek(0)
    assert read_value(buf) is True


def test_write_value_bool_false():
    from tinkercat.graphbinary import write_value, read_value  # ImportError until implemented
    buf = io.BytesIO()
    write_value(buf, False)
    buf.seek(0)
    assert read_value(buf) is False


def test_unsupported_type_raises():
    from tinkercat.graphbinary import write_value  # ImportError until implemented
    with pytest.raises(ValueError):
        write_value(io.BytesIO(), object())


def test_empty_graph_round_trip():
    from tinkercat.graphbinary import write_graph, read_graph  # ImportError until implemented
    g1 = TinkerCat()
    data = write_graph(g1)
    g2 = read_graph(data)
    assert g2.vertex_count == 0
    assert g2.edge_count == 0
    g1.close()
    g2.close()
