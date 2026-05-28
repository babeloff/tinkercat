/**
 * Tests for Task 7.4.1: Merge Steps (mergeV / mergeE).
 * Mirrors tests/python/test_7_4_1_merge_steps.py
 *
 * The JS facade does not expose mergeV/mergeE. These semantics are implemented
 * here as plain JS helpers, mirroring the Kotlin test approach. Tests marked
 * it.todo() document gaps that require facade additions.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex, Edge } from './tinkercat.d.ts'

/** upsert a vertex: find by matchKey/value, create with onCreate if absent. */
function mergeV(
  graph: TinkerCat,
  matchKey: string,
  matchValue: unknown,
  onCreate: Record<string, unknown> = {}
): Vertex {
  const existing = (tc.getAllVertices(graph) as Vertex[]).find(
    (v: Vertex) => tc.getPropertyValue(v, matchKey) === matchValue
  )
  if (existing) return existing
  return tc.addVertexWithLabel(graph, (onCreate.label as string) ?? 'vertex', {
    [matchKey]: matchValue,
    ...onCreate,
  })
}

/** upsert an edge: find by label+endpoints, create if absent. */
function mergeE(
  graph: TinkerCat,
  label: string,
  outVertex: Vertex,
  inVertex: Vertex,
  onCreate: Record<string, unknown> = {}
): Edge {
  const existing = (tc.getVertexEdges(outVertex, 'OUT', [label]) as Edge[]).find(
    (e: Edge) => e.inVertex().id() === inVertex.id()
  )
  if (existing) return existing
  return tc.addEdge(outVertex, label, inVertex, onCreate)
}

describe('Merge Steps', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('mergeV creates vertex when absent', () => {
    mergeV(graph, 'name', 'Alice', { label: 'person' })
    expect(tc.getVertexCount(graph)).toBe(1)
  })

  it('mergeV returns existing vertex without duplicate', () => {
    mergeV(graph, 'name', 'Alice', { label: 'person' })
    mergeV(graph, 'name', 'Alice', { label: 'person' })
    expect(tc.getVertexCount(graph)).toBe(1)
  })

  it('mergeV returns the matched vertex', () => {
    const v1 = mergeV(graph, 'name', 'Bob', { label: 'person' })
    const v2 = mergeV(graph, 'name', 'Bob', { label: 'person' })
    expect(v1.id()).toBe(v2.id())
  })

  it('mergeV with different keys creates distinct vertices', () => {
    mergeV(graph, 'name', 'Alice', { label: 'person' })
    mergeV(graph, 'name', 'Bob',   { label: 'person' })
    expect(tc.getVertexCount(graph)).toBe(2)
  })

  it('mergeE creates edge when absent', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    mergeE(graph, 'knows', a, b)
    expect(tc.getEdgeCount(graph)).toBe(1)
  })

  it('mergeE does not create duplicate edge', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    mergeE(graph, 'knows', a, b)
    mergeE(graph, 'knows', a, b)
    expect(tc.getEdgeCount(graph)).toBe(1)
  })

  it('mergeE returns existing edge', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    const e1 = mergeE(graph, 'knows', a, b)
    const e2 = mergeE(graph, 'knows', a, b)
    expect(e1.id()).toBe(e2.id())
  })

  it('mergeE with different labels creates two edges', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    mergeE(graph, 'knows',   a, b)
    mergeE(graph, 'created', a, b)
    expect(tc.getEdgeCount(graph)).toBe(2)
  })

  it('mergeV via traversal facade', () => {
    // mergeV traversal step is not in the JS facade — calling it throws TypeError
    const v = (tc as any).mergeV(graph, { name: 'Alice' }, { label: 'person' })
    expect(tc.getVertexCount(graph)).toBe(1)
  })

  it('mergeE via traversal facade', () => {
    // mergeE traversal step is not in the JS facade — calling it throws TypeError
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'B' })
    const e = (tc as any).mergeE(graph, a, 'knows', b, {})
    expect(tc.getEdgeCount(graph)).toBe(1)
  })
})
