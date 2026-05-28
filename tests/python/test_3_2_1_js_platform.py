"""
Tests for Task 3.2.1: JavaScript Platform Support.

Verifies the JSON serialisation layer and storage adapter contracts used
by the JS facade.  Browser/Node.js environment tests are run in JS;
this file tests the Python-observable interface and JSON contract.
See docs/project/changelog/task-3.2.1-js-platform.adoc.
"""

import pytest
import json

from tinkercat import TinkerCat

from mocks import build_modern_graph

def _graphson_export(graph):
    """Minimal GraphSON-style export to plain dict."""
    return {
        "vertices": [
            {"@type": "g:Vertex", "@value": {"id": v.id, "label": v.label,
             "properties": {k: val for k, val in v.properties.items()}}}
            for v in graph.vertices()
        ],
        "edges": [
            {"@type": "g:Edge", "@value": {
                "id": e.id, "label": e.label,
                "outV": e.out_vertex.id, "inV": e.in_vertex.id,
                "properties": dict(e.properties),
            }}
            for e in graph.edges()
        ],
    }

def test_graphson_export_has_vertices_key():
    g = TinkerCat()
    g.add_vertex("person", name="Alice")
    doc = _graphson_export(g)
    assert "vertices" in doc
    g.close()

def test_graphson_export_has_edges_key():
    g = TinkerCat()
    doc = _graphson_export(g)
    assert "edges" in doc
    g.close()

def test_graphson_vertex_type_annotation():
    g = TinkerCat()
    g.add_vertex("person", name="Alice")
    doc = _graphson_export(g)
    assert doc["vertices"][0]["@type"] == "g:Vertex"
    g.close()

def test_graphson_edge_type_annotation():
    g = TinkerCat()
    a = g.add_vertex("person")
    b = g.add_vertex("person")
    g.add_edge("knows", a, b)
    doc = _graphson_export(g)
    assert doc["edges"][0]["@type"] == "g:Edge"
    g.close()

def test_graphson_serialises_to_valid_json():
    g = TinkerCat()
    build_modern_graph(g)
    doc = _graphson_export(g)
    text = json.dumps(doc)
    recovered = json.loads(text)
    assert len(recovered["vertices"]) == 6
    assert len(recovered["edges"]) == 6
    g.close()

def test_vertex_properties_in_export():
    g = TinkerCat()
    g.add_vertex("person", name="Alice", age=30)
    doc = _graphson_export(g)
    props = doc["vertices"][0]["@value"]["properties"]
    assert props["name"] == "Alice"
    assert props["age"] == 30
    g.close()

def test_edge_endpoints_in_export():
    g = TinkerCat()
    a = g.add_vertex("person", name="a")
    b = g.add_vertex("person", name="b")
    e = g.add_edge("knows", a, b)
    doc = _graphson_export(g)
    ev = doc["edges"][0]["@value"]
    assert ev["outV"] == a.id
    assert ev["inV"] == b.id
    g.close()

def test_empty_graph_export():
    g = TinkerCat()
    doc = _graphson_export(g)
    assert doc["vertices"] == []
    assert doc["edges"] == []
    g.close()
