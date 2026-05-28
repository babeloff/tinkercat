/**
 * Tests for Task 7.4.6: Discard Step.
 * Mirrors tests/python/test_7_4_6_discard_step.py
 *
 * The JS facade has no discard() traversal step. Side effects are demonstrated
 * via plain JS; traversal-step forms are it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'
import { buildModernGraph } from './helpers'

describe('Discard Step', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('removing all vertices empties the graph', () => {
    buildModernGraph(graph)
    const verts: Vertex[] = tc.getAllVertices(graph)
    for (const v of verts) v.remove()
    expect(tc.getVertexCount(graph)).toBe(0)
  })

  it('side-effect counter increments during iteration', () => {
    buildModernGraph(graph)
    let count = 0
    const verts: Vertex[] = tc.getAllVertices(graph)
    for (const _v of verts) { count++ }
    expect(count).toBe(6)
  })

  it('clearGraph removes all vertices and edges', () => {
    buildModernGraph(graph)
    tc.clearGraph(graph)
    expect(tc.getVertexCount(graph)).toBe(0)
    expect(tc.getEdgeCount(graph)).toBe(0)
  })

  it('iteration result can be discarded (returns undefined)', () => {
    buildModernGraph(graph)
    const result = (tc.getAllVertices(graph) as Vertex[]).forEach(() => {/* side effect only */})
    expect(result).toBeUndefined()
  })

  it('discard() step is not in JS facade', () => {
    expect(typeof (tc as any).discard).toBe('undefined')
  })

  it('V().discard() traversal step', () => {
    // discardTraversal is not in the JS facade — calling it throws TypeError
    buildModernGraph(graph)
    const result = (tc as any).discardTraversal(graph)
    expect(result).toBeUndefined()
  })

  it('V().side_effect().discard() traversal step', () => {
    // discardTraversal with side-effect is not in the JS facade — calling it throws TypeError
    buildModernGraph(graph)
    let count = 0
    const sideEffect = () => { count++ }
    const result = (tc as any).discardTraversalWithSideEffect(graph, sideEffect)
    expect(result).toBeUndefined()
    expect(count).toBe(6)
  })
})
