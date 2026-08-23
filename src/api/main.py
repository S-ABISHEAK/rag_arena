import tempfile
import time
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.api import resources
from src.api.converters import build_query_result
from src.api.health import get_all_health
from src.api.ragas_normalize import normalize_ragas_result
from src.api.schemas import (
    BenchmarkResult,
    CacheLookupResult,
    ConnectionHealth,
    GraphNodesResult,
    IndexResult,
    IndexStatus,
    ModelConfig,
    PageSummary,
    QueryResult,
    QuestionRequest,
    RagasRequest,
    RagasScore,
    ResetResult,
    RewardHistoryEntry,
    RouteResult,
    StrategyScore,
)
from src.config.settings import settings
from src.evaluation.benchmark import compare_rags
from src.vectorstores.qdrant_store import QdrantStore

app = FastAPI(title="RAG Arena API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5183",
        "http://localhost:5173",
        "http://127.0.0.1:5183",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_query(build_rag, question: str, fallback_type: str) -> QueryResult:
    try:
        rag = build_rag()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        start = time.perf_counter()
        raw = rag.query(question)
        elapsed = time.perf_counter() - start
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return build_query_result(raw, fallback_type, elapsed)


# ---- System ----


@app.get("/health", response_model=list[ConnectionHealth])
def health():
    return get_all_health()


@app.get("/config", response_model=ModelConfig)
def config():
    return ModelConfig(
        llm_model=settings.DEFAULT_LLM_MODEL,
        embedding_model=settings.EMBEDDING_MODEL,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        top_k=settings.TOP_K,
        qdrant_collection=settings.QDRANT_COLLECTION,
    )


# ---- Indexing ----


@app.get("/index/status", response_model=IndexStatus)
def index_status():
    chunk_count = len(resources.get_document_registry().load_documents())
    page_count = len(resources.get_page_registry().get_all_pages())

    graph = resources.get_graph_registry().load_graph()
    node_count = graph.node_count() if graph else 0
    edge_count = graph.edge_count() if graph else 0

    return IndexStatus(
        chunk_count=chunk_count,
        page_count=page_count,
        graph_node_count=node_count,
        graph_edge_count=edge_count,
    )


@app.post("/index/directory", response_model=IndexResult)
def index_directory():
    try:
        chunks = resources.get_indexer().index_directory()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    resources.invalidate()
    return IndexResult(chunks_indexed=chunks)


@app.post("/index/upload", response_model=IndexResult)
def index_upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        chunks = resources.get_indexer().index_single_pdf(tmp_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    resources.invalidate()
    return IndexResult(chunks_indexed=chunks)


@app.post("/index/reset", response_model=ResetResult)
def index_reset():
    try:
        resources.get_indexer().clear_registry()
        QdrantStore().delete_collection()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    resources.invalidate()
    return ResetResult(ok=True)


# ---- Querying ----


@app.post("/query/traditional", response_model=QueryResult)
def query_traditional(req: QuestionRequest):
    return _run_query(resources.get_traditional_rag, req.question, "traditional")


@app.post("/query/hybrid", response_model=QueryResult)
def query_hybrid(req: QuestionRequest):
    return _run_query(resources.get_hybrid_rag, req.question, "hybrid")


@app.post("/query/pageindex", response_model=QueryResult)
def query_pageindex(req: QuestionRequest):
    return _run_query(resources.get_pageindex_rag, req.question, "pageindex_v2")


@app.post("/query/graph", response_model=QueryResult)
def query_graph(req: QuestionRequest):
    return _run_query(resources.get_graph_rag, req.question, "graph")


@app.post("/query/agentic", response_model=QueryResult)
def query_agentic(req: QuestionRequest):
    return _run_query(resources.get_agentic_rag, req.question, "traditional")


# ---- Routing / Arena ----


@app.post("/router/classify", response_model=RouteResult)
def router_classify(req: QuestionRequest):
    try:
        route = resources.get_router().route(req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return RouteResult(route=route)


@app.post("/router/embedding-scores", response_model=list[StrategyScore])
def router_embedding_scores(req: QuestionRequest):
    try:
        scores = resources.get_embedding_router().route_with_bandit(req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return [StrategyScore(strategy=name, **values) for name, values in scores.items()]


@app.get("/bandit/scores", response_model=list[StrategyScore])
def bandit_scores():
    scores = resources.get_bandit().get_retriever_scores()
    items = [StrategyScore(strategy=name, reward_score=reward) for name, reward in scores.items()]
    items.sort(key=lambda s: s.reward_score, reverse=True)
    return items


@app.get("/bandit/history", response_model=list[RewardHistoryEntry])
def bandit_history():
    history = resources.get_reward_tracker().load_history()
    return [RewardHistoryEntry(**entry) for entry in history]


# ---- Evaluation ----


@app.post("/evaluate/benchmark", response_model=list[BenchmarkResult])
def evaluate_benchmark(req: QuestionRequest):
    try:
        results = compare_rags(
            question=req.question,
            traditional_rag=resources.get_traditional_rag(),
            hybrid_rag=resources.get_hybrid_rag(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return [BenchmarkResult(**asdict(r)) for r in results]


@app.post("/evaluate/ragas", response_model=RagasScore)
def evaluate_ragas(req: RagasRequest):
    try:
        from src.evaluation.ragas_evaluator import RagasEvaluator
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ragas is unavailable: {exc}")

    raw = RagasEvaluator.evaluate_response(req.question, req.answer, req.context)
    return normalize_ragas_result(raw)


# ---- Pages / Graph / Cache ----


@app.get("/pages", response_model=list[PageSummary])
def pages():
    return [
        PageSummary(page_number=p["page_number"], source=p["source"], summary=p["summary"])
        for p in resources.get_page_registry().get_all_pages()
    ]


@app.get("/graph/nodes", response_model=GraphNodesResult)
def graph_nodes():
    graph = resources.get_graph_registry().load_graph()
    if graph is None:
        return GraphNodesResult(nodes=[], edges=[])

    edges = [
        {"source": s, "target": t, "relation": d.get("relation", "")}
        for s, t, d in graph.get_all_edges()
    ]
    return GraphNodesResult(nodes=graph.get_all_nodes(), edges=edges)


@app.get("/cache/lookup", response_model=CacheLookupResult)
def cache_lookup(question: str):
    result = resources.get_query_cache().get(question)
    return CacheLookupResult(cached=result is not None)
