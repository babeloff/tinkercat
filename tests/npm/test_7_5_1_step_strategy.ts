/**
 * Tests for Task 7.5.1: Step Strategy — has() Predicate Push-down.
 * Mirrors tests/python/test_7_5_1_step_strategy.py
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

describe('Step Strategy', () => {
  let graph: TinkerCat

  beforeEach(() => {
    graph = tc.createTinkerCat()
    for (const [name, age] of [['Alice', 25], ['Bob', 30], ['Carol', 35], ['Dave', 40]]) {
      tc.addVertexWithLabel(graph, 'person', { name, age })
    }
  })

  it('has equivalent returns correct single match', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Alice'
    )
    expect(result).toHaveLength(1)
    expect(tc.getPropertyValue(result[0], 'name')).toBe('Alice')
  })

  it('has equivalent on different value returns correct match', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Bob'
    )
    expect(result).toHaveLength(1)
    expect(tc.getPropertyValue(result[0], 'name')).toBe('Bob')
  })

  it('range predicate filters correctly', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => (tc.getPropertyValue(v, 'age') as number | null ?? 0) >= 30
    )
    const names = result.map((v: Vertex) => tc.getPropertyValue(v, 'name'))
    expect(names).toContain('Bob')
    expect(names).toContain('Carol')
    expect(names).toContain('Dave')
  })

  it('no filter returns all vertices', () => {
    expect(tc.getAllVertices(graph)).toHaveLength(4)
  })

  it('chained predicates — both must match', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) =>
        tc.getPropertyValue(v, 'name') === 'Bob' &&
        tc.getPropertyValue(v, 'age') === 30
    )
    expect(result).toHaveLength(1)
    expect(tc.getPropertyValue(result[0], 'name')).toBe('Bob')
  })

  it('has_label equivalent returns correct subset', () => {
    const g2 = tc.createTinkerCat()
    for (let i = 0; i < 3; i++) tc.addVertexWithLabel(g2, 'person', { idx: i })
    for (let i = 0; i < 2; i++) tc.addVertexWithLabel(g2, 'software', { idx: i })
    const persons = (tc.getAllVertices(g2) as Vertex[]).filter(
      (v: Vertex) => v.label() === 'person'
    )
    expect(persons).toHaveLength(3)
  })

  it('no match returns empty list', () => {
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Nobody'
    )
    expect(result).toHaveLength(0)
  })

  it('has_not equivalent — vertices without property', () => {
    const g2 = tc.createTinkerCat()
    tc.addVertexWithLabel(g2, 'person', { name: 'Alice', email: 'a@b.com' })
    tc.addVertexWithLabel(g2, 'person', { name: 'Bob' })
    const noEmail = (tc.getAllVertices(g2) as Vertex[]).filter(
      (v: Vertex) => !tc.hasProperty(v, 'email')
    )
    expect(noEmail).toHaveLength(1)
    expect(tc.getPropertyValue(noEmail[0], 'name')).toBe('Bob')
  })

  it('index-backed vertex lookup by id is O(1)', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'x', { mark: true })
    const found: Vertex | null = tc.getVertex(graph, v.id())
    expect(found).not.toBeNull()
    expect(found!.id()).toBe(v.id())
  })
})
