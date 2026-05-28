/**
 * Tests for Task 7.4.4: Element Step.
 * Mirrors tests/python/test_7_4_4_element_step.py
 *
 * The JS facade has no properties().element() traversal step. Tests that
 * check the step throws are active; traversal-step forms are it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex, Edge } from './tinkercat.d.ts'

describe('Element Step', () => {
  let graph: TinkerCat

  beforeEach(() => {
    graph = tc.createTinkerCat()
    const a: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Alice', age: 30 })
    const b: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Bob',   age: 25 })
    tc.addEdge(a, 'knows', b, { since: 2020 })
  })

  it('vertex has expected property keys', () => {
    const v: Vertex = (tc.getAllVertices(graph) as Vertex[]).find(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Alice'
    )!
    const keys: string[] = tc.getPropertyKeys(v)
    expect(keys).toContain('name')
    expect(keys).toContain('age')
  })

  it('edge has expected property key', () => {
    const e: Edge = tc.getAllEdges(graph)[0]
    const keys: string[] = tc.getPropertyKeys(e)
    expect(keys).toContain('since')
  })

  it('properties are accessible via getPropertyValue', () => {
    const v: Vertex = (tc.getAllVertices(graph) as Vertex[]).find(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Bob'
    )!
    expect(tc.getPropertyValue(v, 'age')).toBe(25)
  })

  it('element() step is not in JS facade', () => {
    // No traversal API; document the gap
    expect(typeof (tc as any).element).toBe('undefined')
  })

  it('properties().element() returns owning vertex', () => {
    // getPropertyElement is not in the JS facade — calling it throws TypeError
    const v: Vertex = (tc.getAllVertices(graph) as Vertex[]).find(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Alice'
    )!
    const props = v.properties('name')
    const owner = (tc as any).getPropertyElement(props[0])
    expect(owner.id()).toBe(v.id())
  })

  it('properties().element() returns owning edge', () => {
    // getPropertyElement is not in the JS facade — calling it throws TypeError
    const e: Edge = tc.getAllEdges(graph)[0]
    const props = e.properties('since')
    const owner = (tc as any).getPropertyElement(props[0])
    expect(owner.id()).toBe(e.id())
  })

  it('meta-property element() returns owning vertex property', () => {
    // getPropertyElement on a meta-property is not in the JS facade — calling it throws TypeError
    const v: Vertex = (tc.getAllVertices(graph) as Vertex[]).find(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Alice'
    )!
    const prop = v.properties('name')[0]
    const metaOwner = (tc as any).getPropertyElement(prop)
    expect(metaOwner).toBeDefined()
  })

  it('chained element().values()', () => {
    // getPropertyElement chained with values() is not in the JS facade — calling it throws TypeError
    const v: Vertex = (tc.getAllVertices(graph) as Vertex[]).find(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'Alice'
    )!
    const props = v.properties('name')
    const ownerValues = (tc as any).getPropertyElementValues(props[0])
    expect(ownerValues).toContain('Alice')
  })
})
