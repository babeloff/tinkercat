"""
Tests for Task 7.6.1: GraphBinary 4.0 Serialisation.

Validates the type-code encoding, round-trip fidelity, and error
handling for all supported types using a mock binary codec.
See docs/project/changelog/task-7.6.1-graphbinary.adoc.
"""

import pytest
import struct
import io

from tinkercat import TinkerCat

from mocks import build_modern_graph

# ---------------------------------------------------------------------------
# Minimal GraphBinary-style codec
# ---------------------------------------------------------------------------

TYPE_INT    = 0x01
TYPE_LONG   = 0x02
TYPE_STRING = 0x03
TYPE_DOUBLE = 0x04
TYPE_FLOAT  = 0x05
TYPE_BOOL   = 0x06
TYPE_NULL   = 0xFE

def write_value(buf: io.BytesIO, value):
    if value is None:
        buf.write(bytes([TYPE_NULL, 0x01]))
        return
    if isinstance(value, bool):
        buf.write(bytes([TYPE_BOOL, 0x00]))
        buf.write(bytes([0x01 if value else 0x00]))
    elif isinstance(value, int) and -(2**31) <= value < 2**31:
        buf.write(bytes([TYPE_INT, 0x00]))
        buf.write(struct.pack(">i", value))
    elif isinstance(value, int):
        buf.write(bytes([TYPE_LONG, 0x00]))
        buf.write(struct.pack(">q", value))
    elif isinstance(value, float):
        buf.write(bytes([TYPE_DOUBLE, 0x00]))
        buf.write(struct.pack(">d", value))
    elif isinstance(value, str):
        encoded = value.encode("utf-8")
        buf.write(bytes([TYPE_STRING, 0x00]))
        buf.write(struct.pack(">I", len(encoded)))
        buf.write(encoded)
    else:
        raise ValueError(f"Unsupported type: {type(value).__name__}")

def read_value(buf: io.BytesIO):
    type_code = buf.read(1)[0]
    null_flag  = buf.read(1)[0]
    if null_flag == 0x01:
        return None
    if type_code == TYPE_BOOL:
        return buf.read(1)[0] != 0
    if type_code == TYPE_INT:
        return struct.unpack(">i", buf.read(4))[0]
    if type_code == TYPE_LONG:
        return struct.unpack(">q", buf.read(8))[0]
    if type_code == TYPE_DOUBLE:
        return struct.unpack(">d", buf.read(8))[0]
    if type_code == TYPE_STRING:
        length = struct.unpack(">I", buf.read(4))[0]
        return buf.read(length).decode("utf-8")
    raise ValueError(f"Unknown type code: 0x{type_code:02x}")

def write_graph(graph) -> bytes:
    buf = io.BytesIO()
    verts = list(graph.vertices())
    buf.write(struct.pack(">I", len(verts)))
    for v in verts:
        write_value(buf, v.id)
        write_value(buf, v.label)
        props = dict(v.properties)
        buf.write(struct.pack(">I", len(props)))
        for k, val in props.items():
            write_value(buf, k)
            write_value(buf, val)
    edges = list(graph.edges())
    buf.write(struct.pack(">I", len(edges)))
    for e in edges:
        write_value(buf, e.id)
        write_value(buf, e.label)
        write_value(buf, e.out_vertex.id)
        write_value(buf, e.in_vertex.id)
    return buf.getvalue()

def read_graph(data: bytes) -> TinkerCat:
    buf = io.BytesIO(data)
    g = TinkerCat()
    n_verts = struct.unpack(">I", buf.read(4))[0]
    id_map = {}
    for _ in range(n_verts):
        vid   = read_value(buf)
        label = read_value(buf)
        n_props = struct.unpack(">I", buf.read(4))[0]
        props = {}
        for _ in range(n_props):
            k = read_value(buf)
            val = read_value(buf)
            props[k] = val
        v = g.add_vertex(label, vertex_id=str(vid) if not isinstance(vid, str) else vid, **props)
        id_map[vid] = v
    n_edges = struct.unpack(">I", buf.read(4))[0]
    for _ in range(n_edges):
        eid    = read_value(buf)
        label  = read_value(buf)
        out_id = read_value(buf)
        in_id  = read_value(buf)
        g.add_edge(label, id_map[out_id], id_map[in_id])
    return g

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_round_trip_vertex_count():
    g1 = TinkerCat()
    build_modern_graph(g1)
    data = write_graph(g1)
    g2 = read_graph(data)
    assert g2.vertex_count == g1.vertex_count
    g1.close()
    g2.close()

def test_round_trip_edge_count():
    g1 = TinkerCat()
    build_modern_graph(g1)
    data = write_graph(g1)
    g2 = read_graph(data)
    assert g2.edge_count == g1.edge_count
    g1.close()
    g2.close()

def test_round_trip_string_property():
    g1 = TinkerCat()
    g1.add_vertex("person", name="Alice")
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert v.value("name") == "Alice"
    g1.close()
    g2.close()

def test_round_trip_int_property():
    g1 = TinkerCat()
    g1.add_vertex("person", age=30)
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert v.value("age") == 30
    g1.close()
    g2.close()

def test_round_trip_float_property():
    g1 = TinkerCat()
    g1.add_vertex("item", score=3.14)
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert abs(v.value("score") - 3.14) < 1e-9
    g1.close()
    g2.close()

def test_round_trip_bool_property():
    g1 = TinkerCat()
    g1.add_vertex("item", active=True)
    data = write_graph(g1)
    g2 = read_graph(data)
    v = next(iter(g2.vertices()))
    assert v.value("active") is True
    g1.close()
    g2.close()

def test_write_value_int():
    buf = io.BytesIO()
    write_value(buf, 42)
    buf.seek(0)
    assert read_value(buf) == 42

def test_write_value_string():
    buf = io.BytesIO()
    write_value(buf, "hello")
    buf.seek(0)
    assert read_value(buf) == "hello"

def test_write_value_bool_true():
    buf = io.BytesIO()
    write_value(buf, True)
    buf.seek(0)
    assert read_value(buf) is True

def test_write_value_bool_false():
    buf = io.BytesIO()
    write_value(buf, False)
    buf.seek(0)
    assert read_value(buf) is False

def test_unsupported_type_raises():
    with pytest.raises(ValueError):
        write_value(io.BytesIO(), object())

def test_empty_graph_round_trip():
    g1 = TinkerCat()
    data = write_graph(g1)
    g2 = read_graph(data)
    assert g2.vertex_count == 0
    assert g2.edge_count == 0
    g1.close()
    g2.close()
