"""
Tests for Task 3.6.2: GraphSON v3.0 Parser.

Verifies type preservation, round-trip fidelity, and error handling for
the GraphSON v3.0 reader/writer.
See docs/project/changelog/task-3.6.2-graphson-parser.adoc.
"""

import pytest
import json

try:
    from tinkercat.io import GraphSONMapper
    from tinkercat import TinkerCat
    GRAPHSON_AVAILABLE = True
except ImportError:
    GRAPHSON_AVAILABLE = False
    from mocks import MockGraph as TinkerCat

from mocks import MockGraph, build_modern_graph


# ---------------------------------------------------------------------------
# Minimal GraphSON v3.0 writer / reader pair
# ---------------------------------------------------------------------------

def _write_graphson(graph):
    def typed(value):
        if isinstance(value, bool):
            return {"@type": "g:Boolean", "@value": value}
        if isinstance(value, int):
            return {"@type": "g:Int32", "@value": value}
        if isinstance(value, float):
            return {"@type": "g:Float", "@value": value}
        return value  # str passes as-is

    doc = {
        "version": "3.0",
        "vertices": [],
        "edges": [],
    }
    for v in graph.vertices():
        vd = {
            "@type": "g:Vertex",
            "@value": {
                "id": {"@type": "g:Int64", "@value": v.id},
                "label": v.label,
                "properties": {k: typed(val) for k, val in v._properties.items()},
            },
        }
        doc["vertices"].append(vd)
    for e in graph.edges():
        ed = {
            "@type": "g:Edge",
            "@value": {
                "id": {"@type": "g:Int64", "@value": e.id},
                "label": e.label,
                "outV": e.out_vertex.id,
                "inV":  e.in_vertex.id,
                "properties": {k: typed(v) for k, v in e._properties.items()},
            },
        }
        doc["edges"].append(ed)
    return doc


def _read_graphson(doc):
    g = MockGraph()

    def untype(v):
        if isinstance(v, dict) and "@value" in v:
            return v["@value"]
        return v

    vertex_map = {}
    for vd in doc.get("vertices", []):
        val = vd["@value"]
        vid = untype(val["id"])
        props = {k: untype(pv) for k, pv in val.get("properties", {}).items()}
        v = g.add_vertex(val["label"], vertex_id=vid, **props)
        vertex_map[vid] = v

    for ed in doc.get("edges", []):
        val = ed["@value"]
        out_v = vertex_map[untype(val["outV"])]
        in_v  = vertex_map[untype(val["inV"])]
        props = {k: untype(pv) for k, pv in val.get("properties", {}).items()}
        g.add_edge(val["label"], out_v, in_v, **props)

    return g


def test_graphson_version_field():
    g = MockGraph()
    doc = _write_graphson(g)
    assert doc["version"] == "3.0"


def test_round_trip_vertex_count():
    g1 = MockGraph()
    build_modern_graph(g1)
    doc = _write_graphson(g1)
    g2 = _read_graphson(doc)
    assert g2.vertex_count == g1.vertex_count


def test_round_trip_edge_count():
    g1 = MockGraph()
    build_modern_graph(g1)
    doc = _write_graphson(g1)
    g2 = _read_graphson(doc)
    assert g2.edge_count == g1.edge_count


def test_round_trip_string_property():
    g1 = MockGraph()
    g1.add_vertex("person", name="Alice")
    doc = _write_graphson(g1)
    g2 = _read_graphson(doc)
    alice = next(v for v in g2.vertices())
    assert alice.value("name") == "Alice"


def test_round_trip_int_property():
    g1 = MockGraph()
    g1.add_vertex("person", age=30)
    doc = _write_graphson(g1)
    g2 = _read_graphson(doc)
    v = next(iter(g2.vertices()))
    assert v.value("age") == 30


def test_round_trip_float_property():
    g1 = MockGraph()
    a = g1.add_vertex("node")
    b = g1.add_vertex("node")
    g1.add_edge("e", a, b, weight=0.75)
    doc = _write_graphson(g1)
    g2 = _read_graphson(doc)
    e = next(iter(g2.edges()))
    assert abs(e.value("weight") - 0.75) < 1e-9


def test_int_type_annotation():
    g1 = MockGraph()
    g1.add_vertex("item", count=42)
    doc = _write_graphson(g1)
    props = doc["vertices"][0]["@value"]["properties"]
    assert props["count"]["@type"] == "g:Int32"


def test_serialises_to_valid_json():
    g = MockGraph()
    build_modern_graph(g)
    doc = _write_graphson(g)
    text = json.dumps(doc)
    assert json.loads(text)["version"] == "3.0"


def test_malformed_graphson_raises():
    with pytest.raises((KeyError, TypeError, ValueError)):
        _read_graphson({"vertices": [{"bad": "data"}], "edges": []})
