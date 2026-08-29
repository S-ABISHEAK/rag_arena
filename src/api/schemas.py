from typing import Optional

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    question: str


class RagasRequest(BaseModel):
    question: str
    answer: str
    context: list[str]


class Source(BaseModel):
    source: str
    page: int
    chunk_id: Optional[str] = None
    snippet: Optional[str] = None


class QueryResult(BaseModel):
    question: str
    answer: str
    retrieval_type: str
    selected_strategy: Optional[str] = None
    latency: Optional[float] = None
    cache_hit: Optional[bool] = None
    sources: Optional[list[Source]] = None
    selected_pages: Optional[list[int]] = None
    context: Optional[str] = None


class StrategyScore(BaseModel):
    strategy: str
    embedding_score: Optional[float] = None
    reward_score: float
    final_score: Optional[float] = None


class RewardHistoryEntry(BaseModel):
    question: str
    retriever: str
    latency: float
    reward: float


class IndexStatus(BaseModel):
    chunk_count: int
    page_count: int
    graph_node_count: int
    graph_edge_count: int


class IndexResult(BaseModel):
    chunks_indexed: int


class ConnectionHealth(BaseModel):
    service: str
    connected: bool
    last_checked: str
    detail: Optional[str] = None


class PageSummary(BaseModel):
    page_number: int
    source: str
    summary: str


class RagasScore(BaseModel):
    faithfulness: Optional[float] = None
    answer_relevancy: Optional[float] = None
    approximate: Optional[bool] = None
    error: Optional[str] = None


class BenchmarkResult(BaseModel):
    rag_name: str
    question: str
    answer: str
    latency: float
    retrieved_chunks: int


class ModelConfig(BaseModel):
    llm_model: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    top_k: int
    qdrant_collection: str
    reasoning_effort: str
    max_output_tokens: int
    max_context_tokens: int


class RouteResult(BaseModel):
    route: str


class CacheLookupResult(BaseModel):
    cached: bool


class ResetResult(BaseModel):
    ok: bool


class GraphNodesResult(BaseModel):
    nodes: list[str]
    edges: list[dict]
