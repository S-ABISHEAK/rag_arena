# RAG strategy instances are rebuilt fresh whenever the underlying index
# changes (see invalidate()), since HybridRAG/PageIndexRAG/GraphRAG all load
# their working data once, in __init__ — a cached instance would silently
# serve stale results after a re-index otherwise.
#
# Every import below is function-local (inside each get_*), not at module
# level. This module is imported unconditionally by main.py at process
# startup — top-level imports here used to pull in the full
# torch/transformers/sentence-transformers stack (via TraditionalRAG /
# DocumentIndexer / EmbeddingRouter -> QdrantStore -> EmbeddingService)
# before uvicorn ever bound a port. On a memory-constrained deploy (e.g.
# Render's free 512MB tier) that was enough to OOM before the health check
# could even reach the process. Deferring the imports to first actual use
# means the read-only routes (/health, /config, /bandit/*, /pages, ...)
# never pay that cost at all, and the embedding-heavy ones only pay it when
# genuinely needed.

import threading

_cache: dict = {}
_cache_lock = threading.Lock()


def _get(key: str, factory):
    if key not in _cache:
        with _cache_lock:
            # Re-check inside the lock: another thread may have finished
            # constructing it while we were waiting.
            if key not in _cache:
                _cache[key] = factory()
    return _cache[key]


def invalidate() -> None:
    with _cache_lock:
        _cache.clear()


def get_indexer():
    from src.pipeline.index_documents import DocumentIndexer
    return _get("indexer", DocumentIndexer)


def get_traditional_rag():
    from src.retrieval.traditional_rag import TraditionalRAG
    return _get("traditional", TraditionalRAG)


def get_hybrid_rag():
    # Not cached: depends on documents present at construction time.
    from src.retrieval.hybrid_rag import HybridRAG
    return HybridRAG()


def get_pageindex_rag():
    # Not cached: depends on the page index present at construction time.
    from src.retrieval.pageindex_rag import PageIndexRAG
    return PageIndexRAG()


def get_graph_rag():
    # Not cached: depends on the graph present at construction time.
    from src.retrieval.graph_rag import GraphRAG
    return GraphRAG()


def get_agentic_rag():
    # Not cached: builds all four strategies fresh, same reason as above.
    from src.agents.agentic_rag import AgenticRAG
    return AgenticRAG()


def get_router():
    from src.agents.router import Router
    return _get("router", Router)


def get_embedding_router():
    from src.agents.embedding_router import EmbeddingRouter
    return _get("embedding_router", EmbeddingRouter)


def get_bandit():
    from src.agents.contextual_bandit import ContextualBandit
    return _get("bandit", ContextualBandit)


def get_reward_tracker():
    from src.agents.reward_tracker import RewardTracker
    return _get("reward_tracker", RewardTracker)


def get_page_registry():
    from src.pageindex.page_registry import PageRegistry
    return _get("page_registry", PageRegistry)


def get_document_registry():
    from src.storage.document_registry import DocumentRegistry
    return _get("document_registry", DocumentRegistry)


def get_graph_registry():
    from src.graph.graph_registry import GraphRegistry
    return _get("graph_registry", GraphRegistry)


def get_query_cache():
    from src.cache.query_cache import QueryCache
    return _get("query_cache", QueryCache)
