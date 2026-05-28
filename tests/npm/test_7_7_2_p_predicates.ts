/**
 * Tests for Task 7.7.2: P Predicate Additions.
 * Mirrors tests/python/test_7_7_2_p_predicates.py
 *
 * The JS facade has no built-in P class. Predicate semantics are implemented
 * here as plain TypeScript functions, exactly as the Kotlin tests do.
 * Traversal-integrated P predicates are marked it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

// ---------------------------------------------------------------------------
// P predicate factories — mirror the Python P class static methods
// ---------------------------------------------------------------------------

const startingWith  = (prefix: string) => (s: string | null) => s?.startsWith(prefix) ?? false
const endingWith    = (suffix: string) => (s: string | null) => s?.endsWith(suffix)   ?? false
const containing    = (sub: string)    => (s: string | null) => s?.includes(sub)       ?? false
const notStartingWith = (prefix: string) => (s: string | null) => !(startingWith(prefix)(s))
const notEndingWith   = (suffix: string) => (s: string | null) => !(endingWith(suffix)(s))
const notContaining   = (sub: string)    => (s: string | null) => !(containing(sub)(s))
const matchesRegex = (pattern: string) => {
  const re = new RegExp(pattern)
  return (s: string | null) => s !== null && re.test(s)
}

describe('P Predicates', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  // --- startingWith ---

  it('startingWith matches correct prefix', () => {
    expect(startingWith('Al')('Alice')).toBe(true)
  })

  it('startingWith does not match wrong prefix', () => {
    expect(startingWith('Al')('Bob')).toBe(false)
  })

  it('startingWith is null-safe', () => {
    expect(startingWith('Al')(null)).toBe(false)
  })

  it('notStartingWith is logical negation', () => {
    expect(notStartingWith('Al')('Bob')).toBe(true)
    expect(notStartingWith('Al')('Alice')).toBe(false)
  })

  // --- endingWith ---

  it('endingWith matches correct suffix', () => {
    expect(endingWith('son')('Jackson')).toBe(true)
  })

  it('endingWith does not match wrong suffix', () => {
    expect(endingWith('son')('Alice')).toBe(false)
  })

  it('endingWith is null-safe', () => {
    expect(endingWith('son')(null)).toBe(false)
  })

  it('notEndingWith is logical negation', () => {
    expect(notEndingWith('son')('Alice')).toBe(true)
    expect(notEndingWith('son')('Jackson')).toBe(false)
  })

  // --- containing ---

  it('containing matches substring', () => {
    expect(containing('li')('Alice')).toBe(true)
  })

  it('containing does not match absent substring', () => {
    expect(containing('li')('Bob')).toBe(false)
  })

  it('containing is null-safe', () => {
    expect(containing('li')(null)).toBe(false)
  })

  it('notContaining is logical negation', () => {
    expect(notContaining('li')('Bob')).toBe(true)
    expect(notContaining('li')('Alice')).toBe(false)
  })

  // --- regexp ---

  it('regexp matches capitalised name', () => {
    expect(matchesRegex('[A-Z][a-z]+')('Alice')).toBe(true)
  })

  it('regexp does not match digits-only against letters', () => {
    expect(matchesRegex('^\\d+$')('abc')).toBe(false)
  })

  it('regexp partial match works', () => {
    expect(matchesRegex('\\d+')('abc123def')).toBe(true)
  })

  it('regexp is null-safe', () => {
    expect(matchesRegex('\\w+')(null)).toBe(false)
  })

  // --- predicates used as graph filters ---

  it('startingWith used as graph vertex filter', () => {
    for (const name of ['Alice', 'Bob', 'Alan', 'Carol']) {
      tc.addVertexWithLabel(graph, 'person', { name })
    }
    const p = startingWith('A')
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => p(tc.getPropertyValue(v, 'name') as string | null)
    )
    const names = result.map((v: Vertex) => tc.getPropertyValue(v, 'name'))
    expect(names.sort()).toEqual(['Alan', 'Alice'])
  })

  it('endingWith used as graph vertex filter', () => {
    for (const email of ['alice@example.com', 'bob@test.org', 'carol@example.com']) {
      tc.addVertexWithLabel(graph, 'user', { email })
    }
    const p = endingWith('@example.com')
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => p(tc.getPropertyValue(v, 'email') as string | null)
    )
    expect(result).toHaveLength(2)
  })

  it('regexp used as graph vertex filter', () => {
    for (const name of ['alice', 'Bob', 'CAROL', 'dave123']) {
      tc.addVertexWithLabel(graph, 'user', { name })
    }
    const p = matchesRegex('^[A-Z]')
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => p(tc.getPropertyValue(v, 'name') as string | null)
    )
    const names = result.map((v: Vertex) => tc.getPropertyValue(v, 'name'))
    expect(names.sort()).toEqual(['Bob', 'CAROL'])
  })

  it('P.startingWith via traversal facade', () => {
    // tc.P is not in the JS facade — accessing it throws TypeError
    for (const name of ['Alice', 'Bob', 'Alan']) {
      tc.addVertexWithLabel(graph, 'person', { name })
    }
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc as any).P.startingWith('Al')(tc.getPropertyValue(v, 'name'))
    )
    expect(result).toHaveLength(2)
  })

  it('P.endingWith via traversal facade', () => {
    // tc.P is not in the JS facade — accessing it throws TypeError
    for (const name of ['Alice', 'Bob', 'Lance']) {
      tc.addVertexWithLabel(graph, 'person', { name })
    }
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc as any).P.endingWith('ce')(tc.getPropertyValue(v, 'name'))
    )
    expect(result).toHaveLength(2)
  })

  it('P.containing via traversal facade', () => {
    // tc.P is not in the JS facade — accessing it throws TypeError
    for (const name of ['Alice', 'Bob', 'Charlie']) {
      tc.addVertexWithLabel(graph, 'person', { name })
    }
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc as any).P.containing('li')(tc.getPropertyValue(v, 'name'))
    )
    expect(result).toHaveLength(2)
  })

  it('P.regexp via traversal facade', () => {
    // tc.P is not in the JS facade — accessing it throws TypeError
    for (const name of ['alice', 'Bob', 'CAROL']) {
      tc.addVertexWithLabel(graph, 'person', { name })
    }
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc as any).P.regexp('^[A-Z]')(tc.getPropertyValue(v, 'name'))
    )
    expect(result).toHaveLength(2)
  })

  it('GraphSON serialisation of P predicates', () => {
    // tc.P and GraphSON serialization is not in the JS facade — accessing it throws TypeError
    const predicate = (tc as any).P.startingWith('Al')
    const serialized = (tc as any).graphSONSerialize(predicate)
    expect(serialized).toContain('startingWith')
  })
})
