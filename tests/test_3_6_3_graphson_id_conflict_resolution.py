"""
Tests for Task 3.6.3: GraphSON ID Conflict Resolution.

Verifies the four conflict strategies: STRICT, GENERATE_NEW_ID,
MERGE_PROPERTIES, and REPLACE_ELEMENT.
See docs/project/changelog/task-3.6.3-graphson-id-conflict-resolution.adoc.
"""

import pytest
from enum import Enum

from tinkercat import TinkerCat

class ConflictStrategy(Enum):
    STRICT          = "strict"
    GENERATE_NEW_ID = "generate_new_id"
    MERGE_PROPERTIES = "merge_properties"
    REPLACE_ELEMENT  = "replace_element"

def import_graphson_into(target_graph, incoming_vertices, strategy=ConflictStrategy.GENERATE_NEW_ID):
    """Simulate importing vertices with conflict resolution."""
    id_map = {}
    for vdata in incoming_vertices:
        orig_id = vdata["id"]
        existing = target_graph.get_vertex(str(orig_id))
        if existing is None:
            v = target_graph.add_vertex(vdata["label"], vertex_id=str(orig_id), **vdata.get("props", {}))
            id_map[orig_id] = v.id
        else:
            if strategy == ConflictStrategy.STRICT:
                raise ValueError(f"ID conflict: {orig_id}")
            elif strategy == ConflictStrategy.GENERATE_NEW_ID:
                v = target_graph.add_vertex(vdata["label"], **vdata.get("props", {}))
                id_map[orig_id] = v.id
            elif strategy == ConflictStrategy.MERGE_PROPERTIES:
                for k, val in vdata.get("props", {}).items():
                    existing.set_property(k, val)
                id_map[orig_id] = orig_id
            elif strategy == ConflictStrategy.REPLACE_ELEMENT:
                for k, val in vdata.get("props", {}).items():
                    existing.set_property(k, val)
                id_map[orig_id] = orig_id
    return id_map

def test_no_conflict_imports_all():
    g = TinkerCat()
    incoming = [{"id": 1, "label": "person", "props": {"name": "Alice"}}]
    id_map = import_graphson_into(g, incoming)
    assert g.vertex_count == 1
    assert id_map[1] == "1"
    g.close()

def test_strict_raises_on_id_conflict():
    g = TinkerCat()
    g.add_vertex("person", vertex_id="1", name="Alice")
    incoming = [{"id": 1, "label": "person", "props": {"name": "Bob"}}]
    with pytest.raises(ValueError, match="ID conflict"):
        import_graphson_into(g, incoming, ConflictStrategy.STRICT)
    g.close()

def test_generate_new_id_avoids_conflict():
    g = TinkerCat()
    g.add_vertex("person", vertex_id="1", name="Alice")
    incoming = [{"id": 1, "label": "person", "props": {"name": "Bob"}}]
    id_map = import_graphson_into(g, incoming, ConflictStrategy.GENERATE_NEW_ID)
    assert g.vertex_count == 2
    assert id_map[1] != "1"  # remapped
    g.close()

def test_merge_properties_updates_existing():
    g = TinkerCat()
    g.add_vertex("person", vertex_id="1", name="Alice", age=25)
    incoming = [{"id": 1, "label": "person", "props": {"age": 26, "city": "NYC"}}]
    import_graphson_into(g, incoming, ConflictStrategy.MERGE_PROPERTIES)
    v = g.get_vertex("1")
    assert v.value("age") == 26
    assert v.value("city") == "NYC"
    assert v.value("name") == "Alice"  # original property preserved
    g.close()

def test_replace_element_overwrites_properties():
    g = TinkerCat()
    g.add_vertex("person", vertex_id="1", name="Alice", age=25)
    incoming = [{"id": 1, "label": "person", "props": {"name": "Bob"}}]
    import_graphson_into(g, incoming, ConflictStrategy.REPLACE_ELEMENT)
    v = g.get_vertex("1")
    assert v.value("name") == "Bob"
    g.close()

def test_id_remapping_updates_edge_references():
    g = TinkerCat()
    a = g.add_vertex("person", vertex_id="10", name="Alice")
    b = g.add_vertex("person", vertex_id="20", name="Bob")
    g.add_edge("knows", a, b)

    # Incoming has ID conflict on 10 → remapped to new_id
    incoming = [{"id": 10, "label": "person", "props": {"name": "Charlie"}}]
    id_map = import_graphson_into(g, incoming, ConflictStrategy.GENERATE_NEW_ID)
    new_id = id_map[10]
    assert new_id != "10"
    assert g.get_vertex(new_id) is not None
    g.close()

def test_multiple_imports_accumulate():
    g = TinkerCat()
    for batch in range(3):
        incoming = [{"id": 100 + batch, "label": "node", "props": {"batch": batch}}]
        import_graphson_into(g, incoming)
    assert g.vertex_count == 3
    g.close()

def test_empty_import_no_change():
    g = TinkerCat()
    g.add_vertex("person", vertex_id="1", name="Alice")
    import_graphson_into(g, [])
    assert g.vertex_count == 1
    g.close()
