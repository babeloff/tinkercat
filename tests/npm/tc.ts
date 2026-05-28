/**
 * Bridge to the Kotlin/JS facade namespace.
 *
 * The compiled Kotlin/JS UMD module exports functions under a deep namespace:
 *   module.exports.org.apache.tinkerpop.gremlin.tinkercat.js.*
 *
 * This module:
 * 1. Extracts the facade from the deep namespace
 * 2. Patches TinkerVertex/TinkerEdge prototypes with JS-accessible methods
 *    (Kotlin methods are name-mangled in the IR backend; the @JsExport facade
 *    functions are the safe way to call them from JS)
 * 3. Wraps functions that accept Map<String,Any?> (which can't be iterated from
 *    JS) to use the parallel-array variants instead
 * 4. Wraps getGraphStatistics to return a plain JS object
 */

// eslint-disable-next-line @typescript-eslint/no-require-imports
const _pkg = require('tinkercat')
const _raw = _pkg.org.apache.tinkerpop.gremlin.tinkercat.js

// ---------------------------------------------------------------------------
// Prototype patching — run once at module load time
// ---------------------------------------------------------------------------
{
  const _tmpGraph = _raw.createTinkerCat()
  const _vProbe  = _raw.addVertexWithProperty(_tmpGraph, '__probe__', '__probe__')
  const _vProto  = Object.getPrototypeOf(_vProbe) as Record<string, unknown>
  _vProto.label  = function () { return _raw.getLabel(this) }
  _vProto.id     = function () { return _raw.getElementId(this) }
  _vProto.remove = function () { return _raw.removeElement(this) }

  // Patch the edge prototype using addEdgeWithProperty (which works from JS)
  const _eProbe  = _raw.addEdgeWithProperty(_vProbe, '__probe__', _vProbe, '__probe__', '__probe__')
  const _eProto  = Object.getPrototypeOf(_eProbe) as Record<string, unknown>
  _eProto.label     = function () { return _raw.getLabel(this) }
  _eProto.id        = function () { return _raw.getElementId(this) }
  _eProto.remove    = function () { return _raw.removeElement(this) }
  _eProto.inVertex  = function () { return _raw.getInVertex(this) }
  _eProto.outVertex = function () { return _raw.getOutVertex(this) }

  _raw.clearGraph(_tmpGraph)
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Convert a plain JS object to parallel key/value arrays for the Kotlin
// array-based facade functions that avoid Map iteration issues.
function _toArrays(obj: Record<string, unknown>): [string[], unknown[]] {
  const keys = Object.keys(obj)
  return [keys, keys.map(k => obj[k])]
}

// ---------------------------------------------------------------------------
// tc — the wrapped/patched facade
// ---------------------------------------------------------------------------
const tc = {
  ..._raw,

  // Override addVertex to use the array-based variant.
  addVertex(graph: unknown, props: Record<string, unknown> = {}) {
    const [keys, values] = _toArrays(props)
    return _raw.addVertexWithArrays(graph, keys, values)
  },

  // Override addVertexWithLabel to use the array-based variant.
  addVertexWithLabel(graph: unknown, label: string, props: Record<string, unknown> = {}) {
    const [keys, values] = _toArrays(props)
    return _raw.addVertexWithLabelAndArrays(graph, label, keys, values)
  },

  // Override addEdge (with properties object) to use the array-based variant.
  addEdge(outVertex: unknown, label: string, inVertex: unknown, props: Record<string, unknown> = {}) {
    const [keys, values] = _toArrays(props)
    return _raw.addEdgeWithArrays(outVertex, label, inVertex, keys, values)
  },

  // Override getGraphStatistics to return a plain JS object instead of a Kotlin Map.
  getGraphStatistics(graph: unknown) {
    const vertexCount = _raw.getVertexCount(graph) as number
    const edgeCount   = _raw.getEdgeCount(graph) as number
    return {
      vertexCount,
      edgeCount,
      avgDegree: vertexCount > 0 ? (2 * edgeCount) / vertexCount : 0,
      density:   vertexCount > 1 ? (2 * edgeCount) / (vertexCount * (vertexCount - 1)) : 0,
    }
  },
}

export default tc as typeof import('./tinkercat.d.ts') & typeof tc
