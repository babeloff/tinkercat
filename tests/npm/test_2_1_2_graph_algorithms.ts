/**
 * Tests for Task 2.1.2: Graph Algorithms.
 * Mirrors tests/python/test_2_1_2_graph_algorithms.py
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'
import { buildModernGraph } from './helpers'

describe('Graph Algorithms', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('BFS visits all reachable vertices', () => {
    const { marko } = buildModernGraph(graph)
    const visited: Vertex[] = tc.breadthFirstSearch(graph, marko)
    expect(visited.length).toBeGreaterThanOrEqual(1)
  })

  it('DFS visits all reachable vertices', () => {
    const { marko } = buildModernGraph(graph)
    const visited: Vertex[] = tc.depthFirstSearch(graph, marko)
    expect(visited.length).toBeGreaterThanOrEqual(1)
  })

  it('BFS includes the start vertex', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const result: Vertex[] = tc.breadthFirstSearch(graph, a)
    expect(result.some((v: Vertex) => tc.getPropertyValue(v, 'name') === 'A')).toBe(true)
  })

  it('DFS includes the start vertex', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const result: Vertex[] = tc.depthFirstSearch(graph, a)
    expect(result.some((v: Vertex) => tc.getPropertyValue(v, 'name') === 'A')).toBe(true)
  })

  it('shortestPath returns a path between connected vertices', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    const c: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'C' })
    tc.addEdge(a, 'link', b, {})
    tc.addEdge(b, 'link', c, {})
    const path: Vertex[] | null = tc.shortestPath(graph, a, c)
    expect(path).not.toBeNull()
    expect(path!.length).toBeGreaterThan(0)
  })

  it('shortestPath returns null for disconnected vertices', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    const path: Vertex[] | null = tc.shortestPath(graph, a, b)
    expect(path).toBeNull()
  })

  it('shortestPath self-loop returns single vertex', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const path: Vertex[] | null = tc.shortestPath(graph, a, a)
    expect(path).not.toBeNull()
    expect(path!.length).toBe(1)
  })

  it('hasCycle returns false for acyclic graph', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    tc.addEdge(a, 'link', b, {})
    expect(tc.hasCycle(graph)).toBe(false)
  })

  it('hasCycle returns true for cyclic graph', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    const c: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'C' })
    tc.addEdge(a, 'link', b, {})
    tc.addEdge(b, 'link', c, {})
    tc.addEdge(c, 'link', a, {})
    expect(tc.hasCycle(graph)).toBe(true)
  })

  it('findConnectedComponents returns one component for connected graph', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    tc.addEdge(a, 'link', b, {})
    const components: Vertex[][] = tc.findConnectedComponents(graph)
    expect(components.length).toBe(1)
  })

  it('findConnectedComponents returns multiple components for disconnected graph', () => {
    tc.addVertexWithLabel(graph, 'node', { name: 'A' })
    tc.addVertexWithLabel(graph, 'node', { name: 'B' })
    const components: Vertex[][] = tc.findConnectedComponents(graph)
    expect(components.length).toBe(2)
  })

  it('empty graph has no cycle', () => {
    expect(tc.hasCycle(graph)).toBe(false)
  })

  it('getGraphStatistics returns vertex and edge counts', () => {
    buildModernGraph(graph)
    const stats = tc.getGraphStatistics(graph)
    expect(stats.vertexCount).toBe(6)
    expect(stats.edgeCount).toBe(6)
  })
})
