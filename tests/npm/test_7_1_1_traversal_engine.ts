/**
 * Tests for Task 7.1.1: Traversal Engine.
 * Mirrors tests/python/test_7_1_1_traversal_engine.py
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'
import { buildModernGraph } from './helpers'

// Equivalent of g.V().has(key, val).toList()
function filterByProp(graph: TinkerCat, key: string, val: unknown): Vertex[] {
  return (tc.getAllVertices(graph) as Vertex[]).filter(
    (v: Vertex) => tc.getPropertyValue(v, key) === val
  )
}

// Equivalent of g.V().hasLabel(label).toList()
function filterByLabel(graph: TinkerCat, label: string): Vertex[] {
  return (tc.getAllVertices(graph) as Vertex[]).filter(
    (v: Vertex) => v.label() === label
  )
}

describe('Traversal Engine', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('filter by property finds exactly one match', () => {
    buildModernGraph(graph)
    const result = filterByProp(graph, 'name', 'marko')
    expect(result).toHaveLength(1)
    expect(tc.getPropertyValue(result[0], 'name')).toBe('marko')
  })

  it('filter by label returns only persons', () => {
    buildModernGraph(graph)
    const persons = filterByLabel(graph, 'person')
    expect(persons).toHaveLength(4)
  })

  it('filter by label returns only software', () => {
    buildModernGraph(graph)
    const sw = filterByLabel(graph, 'software')
    expect(sw).toHaveLength(2)
  })

  it('values by property returns all matching values', () => {
    buildModernGraph(graph)
    const names = filterByLabel(graph, 'person').map(
      (v: Vertex) => tc.getPropertyValue(v, 'name')
    )
    expect(names).toContain('marko')
    expect(names).toContain('vadas')
    expect(names).toContain('josh')
  })

  it('filter absent property returns empty', () => {
    buildModernGraph(graph)
    const result = filterByProp(graph, 'name', 'nobody')
    expect(result).toHaveLength(0)
  })

  it('outgoing neighbours of marko are correct', () => {
    const { marko } = buildModernGraph(graph)
    const neighbours: Vertex[] = tc.getConnectedVertices(marko, 'OUT')
    const names = neighbours.map((v: Vertex) => tc.getPropertyValue(v, 'name'))
    expect(names).toContain('vadas')
    expect(names).toContain('josh')
    expect(names).toContain('lop')
  })

  it('outgoing edge labels from marko', () => {
    const { marko } = buildModernGraph(graph)
    const edges = tc.getVertexEdges(marko, 'OUT')
    const labels = edges.map((e: { label(): string }) => e.label())
    expect(labels).toContain('knows')
    expect(labels).toContain('created')
  })

  it('count all vertices in modern graph', () => {
    buildModernGraph(graph)
    expect(tc.getVertexCount(graph)).toBe(6)
  })

  it('count all edges in modern graph', () => {
    buildModernGraph(graph)
    expect(tc.getEdgeCount(graph)).toBe(6)
  })

  it('filter by age range', () => {
    buildModernGraph(graph)
    const older = (tc.getAllVertices(graph) as Vertex[]).filter((v: Vertex) => {
      const age = tc.getPropertyValue(v, 'age') as number | null
      return age !== null && age >= 30
    })
    // josh (32) and peter (35)
    expect(older).toHaveLength(2)
  })

  it('filter vertices without a property', () => {
    buildModernGraph(graph)
    const noAge = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => !tc.hasProperty(v, 'age')
    )
    // lop and ripple have no age
    expect(noAge).toHaveLength(2)
  })

  it('incoming neighbours of lop', () => {
    const { lop } = buildModernGraph(graph)
    const inbound: Vertex[] = tc.getConnectedVertices(lop, 'IN')
    // marko, josh, peter all created lop
    expect(inbound).toHaveLength(3)
  })
})
