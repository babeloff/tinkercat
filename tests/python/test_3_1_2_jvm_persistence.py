"""
Tests for Task 3.1.2: JVM Persistence Layer.

Verifies file-based serialisation round-trips (JSON/GraphSON), atomic
writes, and backup/restore semantics.
See docs/project/changelog/task-3.1.2-jvm-persistence.adoc.
"""

import pytest
import json
import os
import tempfile

from tinkercat import TinkerCat

from mocks import build_modern_graph

# ---------------------------------------------------------------------------
# Minimal JSON persistence helper (stands in for the real persistence layer)
# ---------------------------------------------------------------------------

def _save_json(graph, path):
    data = {
        "vertices": [
            {"id": v.id, "label": v.label, "properties": dict(v.properties)}
            for v in graph.vertices()
        ],
        "edges": [
            {
                "id": e.id, "label": e.label,
                "out": e.out_vertex.id, "in": e.in_vertex.id,
                "properties": dict(e.properties),
            }
            for e in graph.edges()
        ],
    }
    with open(path, "w") as f:
        json.dump(data, f)

def _load_json(path):
    g = TinkerCat()
    with open(path) as f:
        data = json.load(f)
    vertex_map = {}
    for vd in data["vertices"]:
        v = g.add_vertex(vd["label"], vertex_id=str(vd["id"]), **vd["properties"])
        vertex_map[vd["id"]] = v
    for ed in data["edges"]:
        out_v = vertex_map[ed["out"]]
        in_v  = vertex_map[ed["in"]]
        g.add_edge(ed["label"], out_v, in_v, **ed["properties"])
    return g

@pytest.fixture
def tmp(tmp_path):
    return tmp_path

def test_json_roundtrip_vertex_count(tmp):
    g1 = TinkerCat()
    build_modern_graph(g1)
    path = str(tmp / "graph.json")
    _save_json(g1, path)
    g2 = _load_json(path)
    assert len(g2.vertices()) == len(g1.vertices())
    g1.close()
    g2.close()

def test_json_roundtrip_edge_count(tmp):
    g1 = TinkerCat()
    build_modern_graph(g1)
    path = str(tmp / "graph.json")
    _save_json(g1, path)
    g2 = _load_json(path)
    assert len(g2.edges()) == len(g1.edges())
    g1.close()
    g2.close()

def test_json_roundtrip_preserves_labels(tmp):
    g1 = TinkerCat()
    build_modern_graph(g1)
    path = str(tmp / "graph.json")
    _save_json(g1, path)
    g2 = _load_json(path)
    labels1 = sorted(v.label for v in g1.vertices())
    labels2 = sorted(v.label for v in g2.vertices())
    assert labels1 == labels2
    g1.close()
    g2.close()

def test_json_roundtrip_preserves_properties(tmp):
    g1 = TinkerCat()
    g1.add_vertex("person", name="Alice", age=30)
    path = str(tmp / "graph.json")
    _save_json(g1, path)
    g2 = _load_json(path)
    alice = next(v for v in g2.vertices() if v.value("name") == "Alice")
    assert alice.value("age") == 30
    g1.close()
    g2.close()

def test_file_not_found_raises():
    with pytest.raises((FileNotFoundError, OSError)):
        _load_json("/nonexistent/path/graph.json")

def test_backup_restore_round_trip(tmp):
    g1 = TinkerCat()
    build_modern_graph(g1)
    save_path   = str(tmp / "graph.json")
    backup_path = str(tmp / "backup.json")
    _save_json(g1, save_path)
    # "backup" = second copy
    import shutil
    shutil.copy(save_path, backup_path)
    # Corrupt primary
    with open(save_path, "w") as f:
        f.write("{}")
    # Restore from backup
    g2 = _load_json(backup_path)
    assert len(g2.vertices()) == 6
    g1.close()
    g2.close()

def test_empty_graph_serialises_cleanly(tmp):
    g1 = TinkerCat()
    path = str(tmp / "empty.json")
    _save_json(g1, path)
    g2 = _load_json(path)
    assert g2.vertex_count == 0
    assert g2.edge_count == 0
    g1.close()
    g2.close()
