/**
 * Type declarations for the TinkerCat JavaScript/TypeScript facade.
 *
 * Generated from src/jsMain/kotlin/TinkerCatFacade.kt via @JsExport.
 * The compiled output lives at build/dist/js/productionLibrary/tinkercat.js.
 * Run `./gradlew jsNodeProductionLibraryDistribution` before running these tests.
 */

export interface GraphElement {
  id(): unknown;
  label(): string;
  keys(): string[];
  /** Returns null when the property is absent. */
  value<T = unknown>(key: string): T | null;
  remove(): void;
}

export interface Vertex extends GraphElement {
  addEdge(label: string, inVertex: Vertex, properties?: Record<string, unknown>): Edge;
  edges(direction: Direction, ...labels: string[]): Iterator<Edge>;
  vertices(direction: Direction, ...labels: string[]): Iterator<Vertex>;
}

export interface Edge extends GraphElement {
  outVertex(): Vertex;
  inVertex(): Vertex;
}

export type Direction = 'OUT' | 'IN' | 'BOTH';

export interface TinkerCat {
  close(): void;
  /** Stub — throws UnsupportedOperationException until transactions are implemented. */
  tx(): TinkerTransaction;
}

export interface TinkerTransaction extends AutoCloseable {
  /** Throws UnsupportedOperationException. */
  open(): never;
  /** Throws UnsupportedOperationException. */
  commit(): never;
  /** Throws UnsupportedOperationException. */
  rollback(): never;
}

// Not a real web API; declared here so TypeScript resolves it.
interface AutoCloseable {
  close(): void;
}

export interface GraphStatistics {
  vertexCount: number;
  edgeCount: number;
  avgDegree: number;
  density: number;
}

// ---------------------------------------------------------------------------
// Facade functions (TinkerCatFacade.kt)
// ---------------------------------------------------------------------------

export declare function createTinkerCat(): TinkerCat;
export declare function createTinkerCatWithSettings(
  allowNullProperties?: boolean,
  defaultCardinality?: 'SINGLE' | 'LIST' | 'SET'
): TinkerCat;

export declare function addVertex(graph: TinkerCat, properties: Record<string, unknown>): Vertex;
export declare function addVertexWithProperty(graph: TinkerCat, key: string, value: unknown): Vertex;
export declare function addVertexWithLabel(graph: TinkerCat, label: string, properties: Record<string, unknown>): Vertex;

export declare function getVertex(graph: TinkerCat, id: unknown): Vertex | null;
export declare function getAllVertices(graph: TinkerCat): Vertex[];
export declare function getVerticesByIds(graph: TinkerCat, ids: unknown[]): Vertex[];

export declare function addEdge(
  outVertex: Vertex,
  label: string,
  inVertex: Vertex,
  properties: Record<string, unknown>
): Edge;
export declare function addEdgeWithProperty(
  outVertex: Vertex,
  label: string,
  inVertex: Vertex,
  propertyKey: string,
  propertyValue: unknown
): Edge;

export declare function getEdge(graph: TinkerCat, id: unknown): Edge | null;
export declare function getAllEdges(graph: TinkerCat): Edge[];

export declare function getVertexEdges(vertex: Vertex, direction: Direction, labels?: string[]): Edge[];
export declare function getConnectedVertices(vertex: Vertex, direction: Direction, labels?: string[]): Vertex[];

export declare function setProperty(element: GraphElement, key: string, value: unknown): unknown;
export declare function getPropertyValue(element: GraphElement, key: string): unknown;
export declare function getPropertyKeys(element: GraphElement): string[];
export declare function hasProperty(element: GraphElement, key: string): boolean;
export declare function getLabel(element: GraphElement): string;
export declare function getElementId(element: GraphElement): unknown;
export declare function removeElement(element: GraphElement): void;
export declare function getInVertex(edge: Edge): Vertex;
export declare function getOutVertex(edge: Edge): Vertex;

export declare function createIndex(graph: TinkerCat, propertyKey: string, elementType: 'Vertex' | 'Edge'): void;
export declare function createCompositeIndex(graph: TinkerCat, propertyKeys: string[], elementType: 'Vertex' | 'Edge'): void;
export declare function createRangeIndex(graph: TinkerCat, propertyKey: string, elementType: 'Vertex' | 'Edge'): void;

export declare function breadthFirstSearch(graph: TinkerCat, startVertex: Vertex): Vertex[];
export declare function depthFirstSearch(graph: TinkerCat, startVertex: Vertex): Vertex[];
export declare function shortestPath(graph: TinkerCat, from: Vertex, to: Vertex): Vertex[] | null;
export declare function findConnectedComponents(graph: TinkerCat): Vertex[][];
export declare function hasCycle(graph: TinkerCat): boolean;

export declare function getVertexCount(graph: TinkerCat): number;
export declare function getEdgeCount(graph: TinkerCat): number;
export declare function clearGraph(graph: TinkerCat): void;
export declare function getGraphStatistics(graph: TinkerCat): GraphStatistics;
