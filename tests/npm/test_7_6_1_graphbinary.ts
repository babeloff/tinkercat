/**
 * Tests for Task 7.6.1: GraphBinary Serialization.
 * Mirrors tests/python/test_7_6_1_graphbinary.py
 *
 * The JS facade has no GraphBinary codec. JSON serialization via toJSON()
 * (from TinkerCatJSAdapter) is available but not exported from the facade.
 * Binary serialization is marked it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'
import { buildModernGraph } from './helpers'

describe('GraphBinary Serialization', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('graphbinary write_graph is not in JS facade', () => {
    expect(typeof (tc as any).writeBinary).toBe('undefined')
    expect(typeof (tc as any).readBinary).toBe('undefined')
  })

  it('graph statistics can be serialized to JSON natively', () => {
    buildModernGraph(graph)
    const stats = tc.getGraphStatistics(graph)
    const json = JSON.stringify(stats)
    expect(json).toContain('vertexCount')
    expect(json).toContain('edgeCount')
  })

  it('vertex property values can be serialized to JSON', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Alice', age: 30 })
    const data = {
      id: v.id(),
      label: v.label(),
      name: tc.getPropertyValue(v, 'name'),
      age: tc.getPropertyValue(v, 'age'),
    }
    const json = JSON.stringify(data)
    expect(JSON.parse(json).name).toBe('Alice')
    expect(JSON.parse(json).age).toBe(30)
  })

  it('round-trip via JSON preserves vertex count', () => {
    buildModernGraph(graph)
    const stats = tc.getGraphStatistics(graph)
    const json = JSON.stringify(stats)
    const parsed = JSON.parse(json)
    expect(parsed.vertexCount).toBe(6)
    expect(parsed.edgeCount).toBe(6)
  })

  it('write_graph produces non-empty bytes', () => {
    // writeGraph binary serialization is not in the JS facade — calling it throws TypeError
    buildModernGraph(graph)
    const bytes = (tc as any).writeGraph(graph)
    expect(bytes.length).toBeGreaterThan(0)
  })

  it('read_graph recreates the same vertex count', () => {
    // writeGraph/readGraph binary serialization is not in the JS facade — calling it throws TypeError
    buildModernGraph(graph)
    const bytes = (tc as any).writeGraph(graph)
    const g2 = (tc as any).readGraph(bytes)
    expect(tc.getVertexCount(g2)).toBe(6)
  })

  it('round-trip preserves vertex properties', () => {
    // writeGraph/readGraph binary serialization is not in the JS facade — calling it throws TypeError
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Alice', age: 30 })
    const bytes = (tc as any).writeGraph(graph)
    const g2 = (tc as any).readGraph(bytes)
    const vertices: Vertex[] = tc.getAllVertices(g2)
    const names = vertices.map((v: Vertex) => tc.getPropertyValue(v, 'name'))
    expect(names).toContain('Alice')
  })

  it('round-trip preserves edge labels', () => {
    // writeGraph/readGraph binary serialization is not in the JS facade — calling it throws TypeError
    buildModernGraph(graph)
    const bytes = (tc as any).writeGraph(graph)
    const g2 = (tc as any).readGraph(bytes)
    const edges = tc.getAllEdges(g2)
    const labels = edges.map((e: any) => e.label())
    expect(labels).toContain('knows')
  })

  it('read_graph with truncated bytes raises', () => {
    // readGraph binary serialization is not in the JS facade — calling it throws TypeError
    buildModernGraph(graph)
    const bytes = (tc as any).writeGraph(graph)
    const truncated = bytes.slice(0, 4)
    expect(() => (tc as any).readGraph(truncated)).toThrow()
  })

  it('empty graph serializes and deserializes', () => {
    // writeGraph/readGraph binary serialization is not in the JS facade — calling it throws TypeError
    const bytes = (tc as any).writeGraph(graph)
    const g2 = (tc as any).readGraph(bytes)
    expect(tc.getVertexCount(g2)).toBe(0)
    expect(tc.getEdgeCount(g2)).toBe(0)
  })
})
