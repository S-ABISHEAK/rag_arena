// Single typed API client. Every screen/component talks to the backend only
// through the functions exported here — all of them hit the real FastAPI
// backend (see src/api/main.py in the repo root's Python project). There is
// no mock data layer: an unreachable backend or a genuine backend error
// (e.g. no GROQ_API_KEY configured) surfaces as a thrown Error, not a
// fabricated success.

import type {
  BenchmarkResult,
  CacheLookupResult,
  ConnectionHealth,
  GraphNodesResult,
  IndexResult,
  IndexStatus,
  ModelConfig,
  PageSummary,
  QueryResult,
  RagasScore,
  ResetResult,
  RetrievalType,
  RewardHistoryEntry,
  RouteResult,
  StrategyScore,
} from "./types"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

// The only strategies that can actually be dispatched to. The embedding
// router's profile set (backend router_profiles.py) includes extra
// categories such as "AGENTIC" that aren't wired to a runnable strategy —
// those are filtered out here rather than displayed as if they were a
// real option.
const RUNNABLE_STRATEGIES = new Set(["TRADITIONAL", "HYBRID", "PAGEINDEX", "GRAPH"])

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
      ...options,
    })
  } catch {
    throw new Error(`Could not reach the backend at ${API_BASE}. Is it running?`)
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      // response wasn't JSON — keep the statusText
    }
    throw new Error(detail)
  }

  return res.json()
}

function postJSON<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) })
}

// ---- Indexing ----

export async function indexDirectory(): Promise<IndexResult> {
  return postJSON<IndexResult>("/index/directory", {})
}

export async function indexUpload(file: File): Promise<IndexResult> {
  const form = new FormData()
  form.append("file", file)

  let res: Response
  try {
    res = await fetch(`${API_BASE}/index/upload`, { method: "POST", body: form })
  } catch {
    throw new Error(`Could not reach the backend at ${API_BASE}. Is it running?`)
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      // not JSON
    }
    throw new Error(detail)
  }

  return res.json()
}

export async function getIndexStatus(): Promise<IndexStatus> {
  return request<IndexStatus>("/index/status")
}

export async function resetIndex(): Promise<ResetResult> {
  return postJSON<ResetResult>("/index/reset", {})
}

// ---- Querying ----

export async function queryTraditional(question: string): Promise<QueryResult> {
  return postJSON<QueryResult>("/query/traditional", { question })
}

export async function queryHybrid(question: string): Promise<QueryResult> {
  return postJSON<QueryResult>("/query/hybrid", { question })
}

export async function queryPageIndex(question: string): Promise<QueryResult> {
  return postJSON<QueryResult>("/query/pageindex", { question })
}

export async function queryGraph(question: string): Promise<QueryResult> {
  return postJSON<QueryResult>("/query/graph", { question })
}

export async function queryAgentic(question: string): Promise<QueryResult> {
  return postJSON<QueryResult>("/query/agentic", { question })
}

export async function queryByStrategy(
  strategy: "traditional" | "hybrid" | "pageindex" | "graph" | "auto",
  question: string
): Promise<QueryResult> {
  switch (strategy) {
    case "traditional":
      return queryTraditional(question)
    case "hybrid":
      return queryHybrid(question)
    case "pageindex":
      return queryPageIndex(question)
    case "graph":
      return queryGraph(question)
    case "auto":
      return queryAgentic(question)
  }
}

// ---- Routing / Arena ----

export async function classifyRoute(question: string): Promise<RouteResult> {
  return postJSON<RouteResult>("/router/classify", { question })
}

export async function embeddingRouterScores(question: string): Promise<StrategyScore[]> {
  const scores = await postJSON<StrategyScore[]>("/router/embedding-scores", { question })
  return scores.filter((s) => RUNNABLE_STRATEGIES.has(s.strategy.toUpperCase()))
}

export async function getBanditScores(): Promise<StrategyScore[]> {
  return request<StrategyScore[]>("/bandit/scores")
}

export async function getRewardHistory(): Promise<RewardHistoryEntry[]> {
  return request<RewardHistoryEntry[]>("/bandit/history")
}

// ---- Evaluation ----

export async function runBenchmark(question: string): Promise<BenchmarkResult[]> {
  return postJSON<BenchmarkResult[]>("/evaluate/benchmark", { question })
}

export async function evaluateRagas(question: string, answer: string, context: string[]): Promise<RagasScore> {
  return postJSON<RagasScore>("/evaluate/ragas", { question, answer, context })
}

// ---- System ----

export async function getConnectionHealth(): Promise<ConnectionHealth[]> {
  return request<ConnectionHealth[]>("/health")
}

export async function cacheLookup(question: string): Promise<CacheLookupResult> {
  return request<CacheLookupResult>(`/cache/lookup?question=${encodeURIComponent(question)}`)
}

export async function getPages(): Promise<PageSummary[]> {
  return request<PageSummary[]>("/pages")
}

export async function getModelConfig(): Promise<ModelConfig> {
  return request<ModelConfig>("/config")
}

export async function getGraphNodes(): Promise<GraphNodesResult> {
  return request<GraphNodesResult>("/graph/nodes")
}

export type { RetrievalType }
