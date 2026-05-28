/**
 * Shared test helpers for TinkerCat TypeScript tests.
 * Mirrors tests/python/mocks.py::build_modern_graph.
 */
import type { TinkerCat, Vertex } from './tinkercat.d.ts'
import tc from './tc'

/**
 * Populate a graph with the standard TinkerPop "modern" toy graph.
 *
 *   marko --knows--> vadas
 *   marko --knows--> josh
 *   marko --created--> lop
 *   josh  --created--> ripple
 *   josh  --created--> lop
 *   peter --created--> lop
 */
export function buildModernGraph(graph: TinkerCat): {
  marko: Vertex; vadas: Vertex; josh: Vertex;
  lop: Vertex; ripple: Vertex; peter: Vertex;
} {
  const marko  = tc.addVertexWithLabel(graph, 'person',   { name: 'marko',  age: 29 })
  const vadas  = tc.addVertexWithLabel(graph, 'person',   { name: 'vadas',  age: 27 })
  const josh   = tc.addVertexWithLabel(graph, 'person',   { name: 'josh',   age: 32 })
  const lop    = tc.addVertexWithLabel(graph, 'software', { name: 'lop',    lang: 'java' })
  const ripple = tc.addVertexWithLabel(graph, 'software', { name: 'ripple', lang: 'java' })
  const peter  = tc.addVertexWithLabel(graph, 'person',   { name: 'peter',  age: 35 })

  tc.addEdge(marko,  'knows',   vadas,  { weight: 0.5 })
  tc.addEdge(marko,  'knows',   josh,   { weight: 1.0 })
  tc.addEdge(marko,  'created', lop,    { weight: 0.4 })
  tc.addEdge(josh,   'created', ripple, { weight: 1.0 })
  tc.addEdge(josh,   'created', lop,    { weight: 0.4 })
  tc.addEdge(peter,  'created', lop,    { weight: 0.2 })

  return { marko, vadas, josh, lop, ripple, peter }
}
