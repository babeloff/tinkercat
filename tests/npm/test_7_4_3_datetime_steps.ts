/**
 * Tests for Task 7.4.3: Datetime Steps.
 * Mirrors tests/python/test_7_4_3_datetime_steps.py
 *
 * The JS facade has no as_date / date_add / date_diff traversal steps.
 * Temporal arithmetic is performed directly in JavaScript; traversal-step
 * forms are marked it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat, Vertex } from './tinkercat.d.ts'

const MS_PER_DAY = 24 * 60 * 60 * 1000

describe('Datetime Steps', () => {
  let graph: TinkerCat
  let eventV: Vertex

  beforeEach(() => {
    graph = tc.createTinkerCat()
    eventV = tc.addVertexWithLabel(graph, 'event', {
      name: 'launch',
      dateStr: '2024-03-15',
      epochMs: new Date('2024-03-15').getTime(),
    })
  })

  it('stored ISO date string round-trips correctly', () => {
    expect(tc.getPropertyValue(eventV, 'dateStr')).toBe('2024-03-15')
  })

  it('stored epoch milliseconds round-trips correctly', () => {
    expect(tc.getPropertyValue(eventV, 'epochMs')).toBe(new Date('2024-03-15').getTime())
  })

  it('adding 7 days to epoch gives correct date', () => {
    const start = tc.getPropertyValue(eventV, 'epochMs') as number
    const end = start + 7 * MS_PER_DAY
    expect(new Date(end).toISOString().startsWith('2024-03-22')).toBe(true)
  })

  it('subtracting 7 days from epoch gives correct date', () => {
    const start = tc.getPropertyValue(eventV, 'epochMs') as number
    const earlier = start - 7 * MS_PER_DAY
    expect(new Date(earlier).toISOString().startsWith('2024-03-08')).toBe(true)
  })

  it('diff between two epoch values gives correct days', () => {
    const a = new Date('2024-01-01').getTime()
    const b = new Date('2024-01-08').getTime()
    const v1: Vertex = tc.addVertexWithLabel(graph, 'span', { epochA: a, epochB: b })
    const diffDays = ((tc.getPropertyValue(v1, 'epochB') as number) -
                      (tc.getPropertyValue(v1, 'epochA') as number)) / MS_PER_DAY
    expect(diffDays).toBe(7)
  })

  it('earlier date is less than later date', () => {
    const d1 = new Date('2020-01-01').getTime()
    const d2 = new Date('2024-01-01').getTime()
    expect(d1).toBeLessThan(d2)
  })

  it('filter events after a threshold date', () => {
    const threshold = new Date('2024-01-01').getTime()
    for (const iso of ['2023-12-31', '2024-06-01', '2025-01-01']) {
      tc.addVertexWithLabel(graph, 'event', { epochMs: new Date(iso).getTime() })
    }
    const future = (tc.getAllVertices(graph) as Vertex[]).filter(v => {
      const ep = tc.getPropertyValue(v, 'epochMs') as number | null
      return ep !== null && ep > threshold
    })
    expect(future.length).toBeGreaterThanOrEqual(2)
  })

  it('as_date traversal step', () => {
    // asDate traversal step is not in the JS facade — calling it throws TypeError
    const result = (tc as any).asDate('2024-03-15')
    expect(result).toBeDefined()
  })

  it('date_add traversal step', () => {
    // dateAdd traversal step is not in the JS facade — calling it throws TypeError
    const result = (tc as any).dateAdd('2024-03-15', 7, 'days')
    expect(new Date(result).toISOString().startsWith('2024-03-22')).toBe(true)
  })

  it('date_diff traversal step', () => {
    // dateDiff traversal step is not in the JS facade — calling it throws TypeError
    const result = (tc as any).dateDiff('2024-03-15', '2024-03-22', 'days')
    expect(result).toBe(7)
  })

  it('unsupported type raises in as_date', () => {
    // asDate traversal step is not in the JS facade — calling it throws TypeError
    // When implemented, passing a non-date value should raise an application error;
    // for now the call itself throws TypeError (not a function) — propagate it uncaught
    const result = (tc as any).asDate(12345)
    // expect an application-level error, not just a TypeError from missing function
    expect(result).toBeNull()
  })
})
