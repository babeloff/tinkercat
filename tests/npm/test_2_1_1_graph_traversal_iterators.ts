/**
 * Tests for Task 2.1.1: Graph Traversal Iterators.
 * Mirrors tests/python/test_2_1_1_graph_traversal_iterators.py
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

describe('Graph Traversal Iterators', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('graph is created empty', () => {
    expect(tc.getVertexCount(graph)).toBe(0)
    expect(tc.getEdgeCount(graph)).toBe(0)
  })

  it('addVertexWithLabel creates a vertex', () => {
    const v = tc.addVertexWithLabel(graph, 'person', { name: 'Alice' })
    expect(v).toBeDefined()
    expect(tc.getVertexCount(graph)).toBe(1)
  })

  it('getAllVertices returns all vertices', () => {
    tc.addVertexWithLabel(graph, 'person', { name: 'Alice' })
    tc.addVertexWithLabel(graph, 'person', { name: 'Bob' })
    const verts: Vertex[] = tc.getAllVertices(graph)
    expect(verts).toHaveLength(2)
  })

  it('vertex has correct label', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Alice' })
    expect(v.label()).toBe('person')
  })

  it('getPropertyValue returns stored string', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Alice' })
    expect(tc.getPropertyValue(v, 'name')).toBe('Alice')
  })

  it('getPropertyValue returns stored number', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Bob', age: 30 })
    expect(tc.getPropertyValue(v, 'age')).toBe(30)
  })

  it('getPropertyValue returns null for absent key', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Carol' })
    expect(tc.getPropertyValue(v, 'missing')).toBeNull()
  })

  it('hasProperty returns true for present key', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Dave' })
    expect(tc.hasProperty(v, 'name')).toBe(true)
  })

  it('hasProperty returns false for absent key', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Eve' })
    expect(tc.hasProperty(v, 'email')).toBe(false)
  })

  it('addEdge creates an edge', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    tc.addEdge(a, 'knows', b, {})
    expect(tc.getEdgeCount(graph)).toBe(1)
  })

  it('getAllEdges returns all edges', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    const c: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'C' })
    tc.addEdge(a, 'knows', b, {})
    tc.addEdge(b, 'knows', c, {})
    expect(tc.getAllEdges(graph)).toHaveLength(2)
  })

  it('getVertexEdges returns outgoing edges', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    tc.addEdge(a, 'knows', b, {})
    const out = tc.getVertexEdges(a, 'OUT')
    expect(out).toHaveLength(1)
    expect(out[0].label()).toBe('knows')
  })

  it('getConnectedVertices returns neighbors', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    tc.addEdge(a, 'knows', b, {})
    const neighbors: Vertex[] = tc.getConnectedVertices(a, 'OUT')
    expect(neighbors).toHaveLength(1)
    expect(tc.getPropertyValue(neighbors[0], 'name')).toBe('B')
  })

  it('vertex removal reduces count', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Alice' })
    v.remove()
    expect(tc.getVertexCount(graph)).toBe(0)
  })

  it('filter vertices by label', () => {
    tc.addVertexWithLabel(graph, 'person',   { name: 'Alice' })
    tc.addVertexWithLabel(graph, 'person',   { name: 'Bob' })
    tc.addVertexWithLabel(graph, 'software', { name: 'lop' })
    const people: Vertex[] = tc.getAllVertices(graph).filter(
      (v: Vertex) => v.label() === 'person'
    )
    expect(people).toHaveLength(2)
  })

  it('filter vertices by property value', () => {
    tc.addVertexWithLabel(graph, 'person', { name: 'Alice', age: 25 })
    tc.addVertexWithLabel(graph, 'person', { name: 'Bob',   age: 40 })
    tc.addVertexWithLabel(graph, 'person', { name: 'Carol', age: 35 })
    const older: Vertex[] = tc.getAllVertices(graph).filter(
      (v: Vertex) => (tc.getPropertyValue(v, 'age') as number) >= 35
    )
    expect(older).toHaveLength(2)
  })
})
