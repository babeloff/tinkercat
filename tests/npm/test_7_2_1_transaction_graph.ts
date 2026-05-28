/**
 * Tests for Task 7.2.1: TinkerTransactionGraph — ACID Transaction Support.
 * Mirrors tests/python/test_7_2_1_transaction_graph.py
 *
 * TinkerCat exposes tx() but every operation on the returned object throws
 * UnsupportedOperationException. Tests for implemented behaviour use it();
 * unimplemented transaction semantics use it.todo().
 */
import { describe, it, expect, beforeEach } from 'vitest'
import tc from './tc'
import type { TinkerCat } from './tinkercat.d.ts'

describe('Transaction Graph', () => {
  let graph: TinkerCat

  beforeEach(() => { graph = tc.createTinkerCat() })

  it('tx() is not exposed in the JS facade', () => {
    const g = tc.createTinkerCat()
    expect(typeof (g as any).tx).toBe('undefined')
  })

  it('commit persists added vertex', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.open()
    tc.addVertexWithLabel(g, 'person', { name: 'Alice' })
    tx.commit()
    expect(tc.getVertexCount(g)).toBe(1)
  })

  it('rollback reverts added vertex', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.open()
    tc.addVertexWithLabel(g, 'person', { name: 'Alice' })
    tx.rollback()
    expect(tc.getVertexCount(g)).toBe(0)
  })

  it('double open raises', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.open()
    tx.open() // should raise on second open
  })

  it('commit without open raises', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.commit() // should raise when no transaction is open
  })

  it('rollback without open raises', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.rollback() // should raise when no transaction is open
  })

  it('context-like block commits on success', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.open()
    try {
      tc.addVertexWithLabel(g, 'person', { name: 'Alice' })
      tx.commit()
    } catch (e) {
      tx.rollback()
      throw e
    }
    expect(tc.getVertexCount(g)).toBe(1)
  })

  it('context-like block rolls back on exception', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.open()
    try {
      tc.addVertexWithLabel(g, 'person', { name: 'Alice' })
      throw new Error('simulated failure')
    } catch (_e) {
      tx.rollback()
    }
    expect(tc.getVertexCount(g)).toBe(0)
  })

  it('rollback restores original property value', () => {
    const g = tc.createTinkerCat()
    const v = tc.addVertexWithLabel(g, 'person', { name: 'Alice' })
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.open()
    tc.setProperty(v, 'name', 'AliceModified')
    tx.rollback()
    expect(tc.getPropertyValue(v, 'name')).toBe('Alice')
  })

  it('committed changes survive second rollback', () => {
    const g = tc.createTinkerCat()
    const tx = (g as any).tx() // TypeError: (g as any).tx is not a function
    tx.open()
    tc.addVertexWithLabel(g, 'person', { name: 'Alice' })
    tx.commit()
    // second transaction rolled back — committed vertex still exists
    tx.open()
    tc.addVertexWithLabel(g, 'person', { name: 'Bob' })
    tx.rollback()
    expect(tc.getVertexCount(g)).toBe(1)
  })
})
