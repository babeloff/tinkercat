/**
 * Tests for Task 7.4.2: String Steps.
 * Mirrors tests/python/test_7_4_2_string_steps.py
 *
 * The JS facade has no to_lower / to_upper / trim / split traversal steps.
 * Equivalent string operations are performed directly in JavaScript, which
 * proves the underlying data is accessible and transformable. Steps that
 * belong in a graph traversal API are marked it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

describe('String Steps', () => {
  let graph: TinkerCat

  beforeEach(() => {
    graph = tc.createTinkerCat()
    for (const name of ['HELLO', 'World', '  spaces  ', 'hello world', 'CamelCase', 'alice', 'BOB', 'Carol', 'dave']) {
      tc.addVertexWithLabel(graph, 'item', { name })
    }
  })

  it('toLower on property values', () => {
    const names = (tc.getAllVertices(graph) as Vertex[])
      .map((v: Vertex) => (tc.getPropertyValue(v, 'name') as string).toLowerCase())
    expect(names).toContain('hello')
    expect(names).toContain('world')
  })

  it('toUpper on property values', () => {
    const names = (tc.getAllVertices(graph) as Vertex[])
      .map((v: Vertex) => (tc.getPropertyValue(v, 'name') as string).toUpperCase())
    expect(names).toContain('HELLO')
    expect(names).toContain('CAMELCASE')
  })

  it('trim removes surrounding whitespace', () => {
    const trimmed = (tc.getAllVertices(graph) as Vertex[])
      .map((v: Vertex) => (tc.getPropertyValue(v, 'name') as string).trim())
    expect(trimmed).toContain('spaces')
  })

  it('split on space', () => {
    const words = (tc.getAllVertices(graph) as Vertex[])
      .flatMap((v: Vertex) => (tc.getPropertyValue(v, 'name') as string).split(' '))
    expect(words).toContain('hello')
    expect(words).toContain('world')
  })

  it('filter by prefix using startsWith', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc.getPropertyValue(v, 'name') as string).startsWith('h')
    )
    expect(result.length).toBeGreaterThanOrEqual(1)
  })

  it('filter by suffix using endsWith', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc.getPropertyValue(v, 'name') as string).endsWith('e')
    )
    expect(result.length).toBeGreaterThanOrEqual(1)
  })

  it('filter by substring using includes', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc.getPropertyValue(v, 'name') as string).includes('amel')
    )
    expect(result).toHaveLength(1)
  })

  it('to_lower traversal step', () => {
    // toLower step in traversal — not yet in the JS facade; calling it throws TypeError
    const result = (tc as any).toLower('HELLO')
    expect(result).toBe('hello')
  })

  it('to_upper traversal step', () => {
    // toUpper step in traversal — not yet in the JS facade; calling it throws TypeError
    const result = (tc as any).toUpper('hello')
    expect(result).toBe('HELLO')
  })

  it('trim traversal step', () => {
    // trim step in traversal — not yet in the JS facade; calling it throws TypeError
    const result = (tc as any).trim('  hello  ')
    expect(result).toBe('hello')
  })

  it('split traversal step', () => {
    // split step in traversal — not yet in the JS facade; calling it throws TypeError
    const result = (tc as any).split('hello world', ' ')
    expect(result).toEqual(['hello', 'world'])
  })

  it('replace traversal step', () => {
    // replace step in traversal — not yet in the JS facade; calling it throws TypeError
    const result = (tc as any).replace('hello world', 'world', 'there')
    expect(result).toBe('hello there')
  })

  it('length traversal step', () => {
    // length step in traversal — not yet in the JS facade; calling it throws TypeError
    const result = (tc as any).length('hello')
    expect(result).toBe(5)
  })
})
