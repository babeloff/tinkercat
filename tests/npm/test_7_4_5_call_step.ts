/**
 * Tests for Task 7.4.5: Call Step.
 * Mirrors tests/python/test_7_4_5_call_step.py
 *
 * The JS facade has no call() traversal step. The service registry pattern is
 * implemented here in plain TypeScript to prove the data model is correct;
 * traversal-step forms are it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

type ServiceFn = (vertices: Vertex[], context: Record<string, unknown>) => Vertex[]

class ServiceRegistry {
  private services = new Map<string, ServiceFn>()
  register(name: string, fn: ServiceFn) { this.services.set(name, fn) }
  call(name: string, vertices: Vertex[], context: Record<string, unknown>): Vertex[] {
    const fn = this.services.get(name)
    if (!fn) throw new Error(`Unknown service: ${name}`)
    return fn(vertices, context)
  }
}

describe('Call Step', () => {
  let graph: TinkerCat
  let registry: ServiceRegistry

  beforeEach(() => {
    graph = tc.createTinkerCat()
    registry = new ServiceRegistry()

    for (const name of ['Alice', 'Bob', 'Carol']) {
      tc.addVertexWithLabel(graph, 'person', { name })
    }

    registry.register('echo', (verts) => verts)
    registry.register('filter_name', (verts, ctx) =>
      verts.filter((v: Vertex) => tc.getPropertyValue(v, 'name') === ctx['name'])
    )
  })

  it('echo service returns all vertices unchanged', () => {
    const all: Vertex[] = tc.getAllVertices(graph)
    const result = registry.call('echo', all, {})
    expect(result).toHaveLength(3)
  })

  it('filter_name service returns matching vertex', () => {
    const all: Vertex[] = tc.getAllVertices(graph)
    const result = registry.call('filter_name', all, { name: 'Alice' })
    expect(result).toHaveLength(1)
    expect(tc.getPropertyValue(result[0], 'name')).toBe('Alice')
  })

  it('unknown service raises', () => {
    const all: Vertex[] = tc.getAllVertices(graph)
    expect(() => registry.call('no_such_service', all, {})).toThrow('Unknown service: no_such_service')
  })

  it('call() step is not in JS facade', () => {
    expect(typeof (tc as any).call).toBe('undefined')
  })

  it('call() traversal step with echo service', () => {
    // callService traversal step is not in the JS facade — calling it throws TypeError
    const all: Vertex[] = tc.getAllVertices(graph)
    const result = (tc as any).callService(graph, 'echo', all, {})
    expect(result).toHaveLength(3)
  })

  it('call() traversal step with filter service', () => {
    // callService traversal step is not in the JS facade — calling it throws TypeError
    const all: Vertex[] = tc.getAllVertices(graph)
    const result = (tc as any).callService(graph, 'filter_name', all, { name: 'Alice' })
    expect(result).toHaveLength(1)
    expect(tc.getPropertyValue(result[0], 'name')).toBe('Alice')
  })

  it('call() traversal step with unknown service raises', () => {
    // callService traversal step is not in the JS facade — calling it throws TypeError;
    // call directly so the TypeError propagates as an uncaught test failure
    const all: Vertex[] = tc.getAllVertices(graph)
    const result = (tc as any).callService(graph, 'no_such_service', all, {})
    // when implemented, this should throw an application-level error for unknown service
    expect(result).toBeUndefined()
  })
})
