/**
 * Tests for Task 7.7.1: Lambda Deprecation.
 * Mirrors tests/python/test_7_7_1_lambda_deprecation.py
 *
 * Validates that standard graph operations work correctly without lambda-based
 * step shortcuts. All filtering is done with plain JS array methods.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'
import { buildModernGraph } from './helpers'

describe('Lambda Deprecation', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('filter by label without lambda shortcuts', () => {
    buildModernGraph(graph)
    const persons = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => v.label() === 'person'
    )
    expect(persons).toHaveLength(4)
  })

  it('filter by property without lambda shortcuts', () => {
    buildModernGraph(graph)
    const result = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => tc.getPropertyValue(v, 'name') === 'marko'
    )
    expect(result).toHaveLength(1)
  })

  it('collect property values without lambda shortcuts', () => {
    buildModernGraph(graph)
    const names = (tc.getAllVertices(graph) as Vertex[])
      .filter((v: Vertex) => v.label() === 'person')
      .map((v: Vertex) => tc.getPropertyValue(v, 'name') as string)
    expect(names.sort()).toEqual(['josh', 'marko', 'peter', 'vadas'])
  })

  it('filter by has_not — vertices without lang property', () => {
    buildModernGraph(graph)
    const noLang = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => !tc.hasProperty(v, 'lang')
    )
    // persons have no lang (4), software have lang (2) → 4 vertices have no lang
    expect(noLang).toHaveLength(4)
  })

  it('filter by property presence without lambda shortcuts', () => {
    buildModernGraph(graph)
    const withAge = (tc.getAllVertices(graph) as Vertex[]).filter(
      (v: Vertex) => tc.hasProperty(v, 'age')
    )
    // marko, vadas, josh, peter all have age
    expect(withAge).toHaveLength(4)
  })

  it('outgoing edges from marko without lambda shortcuts', () => {
    const { marko } = buildModernGraph(graph)
    const edges = tc.getVertexEdges(marko, 'OUT')
    expect(edges).toHaveLength(3)
  })

  it('chained filter and map without lambda shortcuts', () => {
    buildModernGraph(graph)
    const aged30plus = (tc.getAllVertices(graph) as Vertex[])
      .filter((v: Vertex) => {
        const age = tc.getPropertyValue(v, 'age') as number | null
        return age !== null && age >= 30
      })
      .map((v: Vertex) => tc.getPropertyValue(v, 'name') as string)
    expect(aged30plus.sort()).toEqual(['josh', 'peter'])
  })

  it('count without lambda shortcuts matches getVertexCount', () => {
    buildModernGraph(graph)
    const manualCount = (tc.getAllVertices(graph) as Vertex[]).length
    expect(manualCount).toBe(tc.getVertexCount(graph))
  })
})
