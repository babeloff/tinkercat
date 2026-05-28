/**
 * Tests for Task 2.2.1: Multi-property Support.
 * Mirrors tests/python/test_2_2_1_multi_property_support.py
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex, Edge } from './tinkercat.d.ts'

describe('Multi-property Support', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('stores string property', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'item', { name: 'hello' })
    expect(tc.getPropertyValue(v, 'name')).toBe('hello')
  })

  it('stores integer property', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'item', { count: 42 })
    expect(tc.getPropertyValue(v, 'count')).toBe(42)
  })

  it('stores float property', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'item', { score: 3.14 })
    expect(tc.getPropertyValue(v, 'score')).toBeCloseTo(3.14)
  })

  it('stores boolean property', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'item', { active: true })
    expect(tc.getPropertyValue(v, 'active')).toBe(true)
  })

  it('stores multiple properties', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Alice', age: 25, active: true })
    expect(tc.getPropertyValue(v, 'name')).toBe('Alice')
    expect(tc.getPropertyValue(v, 'age')).toBe(25)
    expect(tc.getPropertyValue(v, 'active')).toBe(true)
  })

  it('getPropertyKeys returns all stored keys', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'person', { name: 'Bob', age: 30 })
    const keys: string[] = tc.getPropertyKeys(v)
    expect(keys).toContain('name')
    expect(keys).toContain('age')
  })

  it('property can be updated via setProperty', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'item', { count: 1 })
    tc.setProperty(v, 'count', 99)
    expect(tc.getPropertyValue(v, 'count')).toBe(99)
  })

  it('edge stores properties', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    const e: Edge = tc.addEdge(a, 'link', b, { weight: 0.9 })
    expect(tc.getPropertyValue(e, 'weight')).toBeCloseTo(0.9)
  })

  it('edge label is correct', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    const e: Edge = tc.addEdge(a, 'knows', b, {})
    expect(e.label()).toBe('knows')
  })

  it('vertex id is unique', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    expect(a.id()).not.toBe(b.id())
  })

  it('property keys are case-sensitive', () => {
    const v: Vertex = tc.addVertexWithLabel(graph, 'item', { Name: 'Alice' })
    expect(tc.hasProperty(v, 'Name')).toBe(true)
    expect(tc.hasProperty(v, 'name')).toBe(false)
  })

  it('vertex without label gets default label', () => {
    const v: Vertex = tc.addVertex(graph, { name: 'NoLabel' })
    expect(v.label()).toBeDefined()
  })

  it('large number of vertices is handled', () => {
    for (let i = 0; i < 100; i++) {
      tc.addVertexWithLabel(graph, 'item', { index: i })
    }
    expect(tc.getVertexCount(graph)).toBe(100)
  })
})
