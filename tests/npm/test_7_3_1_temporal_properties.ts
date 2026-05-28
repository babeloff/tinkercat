/**
 * Tests for Task 7.3.1: Temporal Properties.
 * Mirrors tests/python/test_7_3_1_temporal_properties.py
 *
 * TinkerCat stores any JavaScript value as a property. Date objects and ISO
 * strings survive the round-trip because the store treats them opaquely.
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

describe('Temporal Properties', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('stores an ISO date string', () => {
    const iso = '2024-06-15'
    const v: Vertex = tc.addVertexWithLabel(graph, 'event', { date: iso })
    expect(tc.getPropertyValue(v, 'date')).toBe(iso)
  })

  it('stores a Date object as a property', () => {
    const d = new Date('2024-01-01T00:00:00Z')
    const v: Vertex = tc.addVertexWithLabel(graph, 'event', { ts: d })
    expect(tc.getPropertyValue(v, 'ts')).toBeTruthy()
  })

  it('stores epoch milliseconds as a number', () => {
    const epoch = Date.UTC(2024, 0, 1)
    const v: Vertex = tc.addVertexWithLabel(graph, 'event', { epoch })
    expect(tc.getPropertyValue(v, 'epoch')).toBe(epoch)
  })

  it('stores duration as milliseconds', () => {
    const sevenDaysMs = 7 * 24 * 60 * 60 * 1000
    const v: Vertex = tc.addVertexWithLabel(graph, 'task', { durationMs: sevenDaysMs })
    expect(tc.getPropertyValue(v, 'durationMs')).toBe(sevenDaysMs)
  })

  it('earliest date compares less than latest', () => {
    const d1 = new Date('2020-01-01').getTime()
    const d2 = new Date('2024-01-01').getTime()
    expect(d1).toBeLessThan(d2)
  })

  it('stores multiple temporal fields', () => {
    const created = '2024-01-01'
    const updated = '2024-06-15'
    const v: Vertex = tc.addVertexWithLabel(graph, 'record', { created, updated })
    expect(tc.getPropertyValue(v, 'created')).toBe(created)
    expect(tc.getPropertyValue(v, 'updated')).toBe(updated)
  })

  it('duration arithmetic in JS gives correct days', () => {
    const start = new Date('2024-01-01').getTime()
    const end   = new Date('2024-01-08').getTime()
    const days = (end - start) / (1000 * 60 * 60 * 24)
    expect(days).toBe(7)
  })

  it('edge stores a timestamp property', () => {
    const a: Vertex = tc.addVertexWithLabel(graph, 'event', { name: 'A' })
    const b: Vertex = tc.addVertexWithLabel(graph, 'event', { name: 'B' })
    const ts = new Date().toISOString()
    const e  = tc.addEdge(a, 'follows', b, { since: ts })
    expect(tc.getPropertyValue(e, 'since')).toBe(ts)
  })

  it('as_date traversal step', () => {
    // asDate is not in the JS facade yet — calling it throws TypeError
    const result = (tc as any).asDate('2024-01-15')
    expect(result).toBeDefined()
  })

  it('date_add traversal step', () => {
    // dateAdd is not in the JS facade yet — calling it throws TypeError
    const result = (tc as any).dateAdd('2024-01-15', 7, 'days')
    expect(result).toBeDefined()
  })

  it('date_diff traversal step', () => {
    // dateDiff is not in the JS facade yet — calling it throws TypeError
    const result = (tc as any).dateDiff('2024-01-01', '2024-01-08', 'days')
    expect(result).toBe(7)
  })
})
