import logging
import tempfile
import time
from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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
from src.agents.reward_function import RewardFunction
from src.config.settings import settings
from src.evaluation.benchmark import compare_rags
from src.vectorstores.qdrant_store import QdrantStore

# QueryResult.retrieval_type -> the retriever name the bandit/reward
# tracker expects (see ContextualBandit.get_retriever_scores).
_RETRIEVAL_TYPE_TO_RETRIEVER = {
    "traditional": "TRADITIONAL",
    "hybrid": "HYBRID",
    "pageindex_v2": "PAGEINDEX",
    "graph": "GRAPH",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("rag_arena.api")

if not settings.API_KEY:
    # Not fatal — local dev needs no setup — but a deployment running with
    # no gate on /index/*, /query/*, /evaluate/*, /router/* is publicly
    # abusable (index wipes, unlimited Groq-billed queries). Loud on
    # purpose so this is a choice made at deploy time, not an oversight.
    logger.warning(
        "API_KEY is not set — /index, /query, /evaluate, and /router routes "
        "are UNPROTECTED. Set API_KEY before deploying publicly."
    )

app = FastAPI(title="RAG Arena API")


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    # Open by default (empty API_KEY) so local dev needs no header at all.
    # Once API_KEY is set, every dependent route requires a matching
    # X-API-Key header — see the settings.API_KEY docstring for what this
    # does and doesn't protect against.
    if not settings.API_KEY:
        return
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Missing or invalid API key.")


_guarded = [Depends(require_api_key)]

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Safety net for anything that isn't already caught and turned into an
    # HTTPException below — logs the full traceback server-side (nothing
    # here was being logged before, which makes production issues hard to
    # diagnose from logs alone) while still returning the real error detail
    # to the client, consistent with every other error response in this API.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": str(exc)})


def _record_reward(question: str, result: QueryResult) -> None:
    # Cache hits return near-instantly and reflect nothing about the
    # strategy's real retrieval/generation quality or speed — recording
    # them would artificially inflate whichever strategy happens to get
    # cache hits more often. Only real, freshly-run queries feed the bandit.
    if result.cache_hit:
        return

    retriever = _RETRIEVAL_TYPE_TO_RETRIEVER.get(result.retrieval_type)
    if retriever is None or result.latency is None:
        return

    try:
        reward = RewardFunction.compute(result.latency)
        resources.get_reward_tracker().record_result(
            question=question,
            retriever=retriever,
            latency=result.latency,
            reward=reward,
        )
    except Exception:
        # The reward log is observability, not the response itself — a
        # failure here must never break the actual query result.
        logger.exception("Failed to record reward for a %s query", retriever)


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

    result = build_query_result(raw, fallback_type, elapsed)
    _record_reward(question, result)
    return result


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
        reasoning_effort=settings.REASONING_EFFORT,
        max_output_tokens=settings.MAX_OUTPUT_TOKENS,
        max_context_tokens=settings.MAX_CONTEXT_TOKENS,
    )


# ---- Indexing ----


@app.get("/index/status", response_model=IndexStatus)
def index_status():
    try:
        chunk_count = len(resources.get_document_registry().load_documents())
        page_count = len(resources.get_page_registry().get_all_pages())

        graph = resources.get_graph_registry().load_graph()
        node_count = graph.node_count() if graph else 0
        edge_count = graph.edge_count() if graph else 0
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return IndexStatus(
        chunk_count=chunk_count,
        page_count=page_count,
        graph_node_count=node_count,
        graph_edge_count=edge_count,
    )


@app.post("/index/directory", response_model=IndexResult, dependencies=_guarded)
def index_directory():
    try:
        chunks = resources.get_indexer().index_directory()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    resources.invalidate()
    return IndexResult(chunks_indexed=chunks)


UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB read chunks


@app.post("/index/upload", response_model=IndexResult, dependencies=_guarded)
def index_upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    bytes_written = 0
    tmp_path: str | None = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

            # Stream in bounded chunks rather than file.file.read() (which
            # buffers the whole upload in memory) so an oversized upload is
            # rejected before it can exhaust server memory.
            while chunk := file.file.read(UPLOAD_CHUNK_SIZE):
                bytes_written += len(chunk)
                if bytes_written > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB upload limit.",
                    )
                tmp.write(chunk)

        chunks = resources.get_indexer().index_single_pdf(tmp_path)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)

    resources.invalidate()
    return IndexResult(chunks_indexed=chunks)


@app.post("/index/reset", response_model=ResetResult, dependencies=_guarded)
def index_reset():
    try:
        resources.get_indexer().clear_registry()
        QdrantStore().delete_collection()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    resources.invalidate()
    return ResetResult(ok=True)


# ---- Querying ----


@app.post("/query/traditional", response_model=QueryResult, dependencies=_guarded)
def query_traditional(req: QuestionRequest):
    return _run_query(resources.get_traditional_rag, req.question, "traditional")


@app.post("/query/hybrid", response_model=QueryResult, dependencies=_guarded)
def query_hybrid(req: QuestionRequest):
    return _run_query(resources.get_hybrid_rag, req.question, "hybrid")


@app.post("/query/pageindex", response_model=QueryResult, dependencies=_guarded)
def query_pageindex(req: QuestionRequest):
    return _run_query(resources.get_pageindex_rag, req.question, "pageindex_v2")


@app.post("/query/graph", response_model=QueryResult, dependencies=_guarded)
def query_graph(req: QuestionRequest):
    return _run_query(resources.get_graph_rag, req.question, "graph")


@app.post("/query/agentic", response_model=QueryResult, dependencies=_guarded)
def query_agentic(req: QuestionRequest):
    return _run_query(resources.get_agentic_rag, req.question, "traditional")


# ---- Routing / Arena ----


@app.post("/router/classify", response_model=RouteResult, dependencies=_guarded)
def router_classify(req: QuestionRequest):
    try:
        route = resources.get_router().route(req.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return RouteResult(route=route)


@app.post("/router/embedding-scores", response_model=list[StrategyScore], dependencies=_guarded)
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


@app.post("/evaluate/benchmark", response_model=list[BenchmarkResult], dependencies=_guarded)
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


@app.post("/evaluate/ragas", response_model=RagasScore, dependencies=_guarded)
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
