export type RetrievalType = "traditional" | "hybrid" | "pageindex_v2" | "graph"

export type Strategy = "TRADITIONAL" | "HYBRID" | "PAGEINDEX" | "GRAPH"

export type StrategyKey = "traditional" | "hybrid" | "pageindex" | "graph" | "auto"

export interface Source {
  source: string
  page: number
  chunk_id?: string
  snippet?: string
}

export interface QueryResult {
  question: string
  answer: string
  retrieval_type: RetrievalType
  selected_strategy?: string
  latency?: number
  cache_hit?: boolean
  sources?: Source[]
  selected_pages?: number[]
  context?: string
  timestamp?: number
}

export interface StrategyScore {
  // Widened to `string`, not `Strategy`: the embedding router's profile set
  // (router_profiles.py) includes categories like "AGENTIC" that aren't one
  // of the four runnable strategies. Callers filter to known strategies.
  strategy: string
  embedding_score?: number
  reward_score: number
  final_score?: number
}

export interface RewardHistoryEntry {
  question: string
  retriever: Strategy
  latency: number
  reward: number
}

export interface IndexStatus {
  chunk_count: number
  page_count: number
  graph_node_count: number
  graph_edge_count: number
}

export interface ConnectionHealth {
  service: "Qdrant" | "Redis" | "Groq"
  connected: boolean
  last_checked: string
  detail?: string
}

export interface PageSummary {
  page_number: number
  source: string
  summary: string
}

export interface RagasScore {
  faithfulness: number | null
  answer_relevancy: number | null
  approximate?: boolean
  error?: string
}

export interface BenchmarkResult {
  rag_name: string
  question: string
  answer: string
  latency: number
  retrieved_chunks: number
}

export interface ModelConfig {
  llm_model: string
  embedding_model: string
  chunk_size: number
  chunk_overlap: number
  top_k: number
  qdrant_collection: string
}

export interface IndexResult {
  chunks_indexed: number
}

export interface RouteResult {
  route: string
}

export interface CacheLookupResult {
  cached: boolean
}

export interface ResetResult {
  ok: boolean
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
}

export interface GraphNodesResult {
  nodes: string[]
  edges: GraphEdge[]
}
