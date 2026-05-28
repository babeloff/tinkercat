/**
 * Tests for Task 7.5.2: Count Strategy — Short-circuit Count.
 * Mirrors tests/python/test_7_5_2_count_strategy.py
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

describe('Count Strategy', () => {
  let graph: TinkerCat

  beforeEach(() => {
    graph = tc.createTinkerCat()
    for (let i = 0; i < 4; i++) tc.addVertexWithLabel(graph, 'person',   { idx: i })
    for (let i = 0; i < 2; i++) tc.addVertexWithLabel(graph, 'software', { idx: i })
  })

  it('vertex count is correct', () => {
    expect(tc.getVertexCount(graph)).toBe(6)
  })

  it('edge count is zero in vertex-only graph', () => {
    expect(tc.getEdgeCount(graph)).toBe(0)
  })

  it('label count for person is correct', () => {
    const count = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => v.label() === 'person'
    ).length
    expect(count).toBe(4)
  })

  it('label count for software is correct', () => {
    const count = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => v.label() === 'software'
    ).length
    expect(count).toBe(2)
  })

  it('absent label count is zero', () => {
    const count = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => v.label() === 'device'
    ).length
    expect(count).toBe(0)
  })

  it('getVertexCount matches getAllVertices.length', () => {
    expect(tc.getVertexCount(graph)).toBe((tc.getAllVertices(graph) as Vertex[]).length)
  })

  it('count increments after addVertex', () => {
    const before = tc.getVertexCount(graph)
    tc.addVertexWithLabel(graph, 'device', { name: 'x' })
    expect(tc.getVertexCount(graph)).toBe(before + 1)
  })

  it('edge count is correct after adding edges', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'n', { name: 'a' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'n', { name: 'b' })
    tc.addEdge(a, 'link', b, {})
    tc.addEdge(a, 'link', b, {})
    expect(tc.getEdgeCount(graph)).toBe(2)
  })

  it('getVertexCount is consistent with getGraphStatistics', () => {
    const stats = tc.getGraphStatistics(graph)
    expect(stats.vertexCount).toBe(tc.getVertexCount(graph))
    expect(stats.edgeCount).toBe(tc.getEdgeCount(graph))
  })
})
