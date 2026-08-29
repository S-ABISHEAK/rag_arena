# RAG strategy instances are rebuilt fresh whenever the underlying index
# changes (see invalidate()), since HybridRAG/PageIndexRAG/GraphRAG all load
# their working data once, in __init__ — a cached instance would silently
# serve stale results after a re-index otherwise.

import threading

from src.retrieval.traditional_rag import TraditionalRAG
from src.retrieval.hybrid_rag import HybridRAG
from src.retrieval.pageindex_rag import PageIndexRAG
from src.retrieval.graph_rag import GraphRAG
from src.agents.agentic_rag import AgenticRAG
from src.agents.router import Router
from src.agents.embedding_router import EmbeddingRouter
from src.agents.contextual_bandit import ContextualBandit
from src.agents.reward_tracker import RewardTracker
from src.pipeline.index_documents import DocumentIndexer
from src.pageindex.page_registry import PageRegistry
from src.storage.document_registry import DocumentRegistry
from src.graph.graph_registry import GraphRegistry
from src.cache.query_cache import QueryCache

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


def get_indexer() -> DocumentIndexer:
    return _get("indexer", DocumentIndexer)


def get_traditional_rag() -> TraditionalRAG:
    return _get("traditional", TraditionalRAG)


def get_hybrid_rag() -> HybridRAG:
    # Not cached: depends on documents present at construction time.
    return HybridRAG()


def get_pageindex_rag() -> PageIndexRAG:
    # Not cached: depends on the page index present at construction time.
    return PageIndexRAG()


def get_graph_rag() -> GraphRAG:
    # Not cached: depends on the graph present at construction time.
    return GraphRAG()


def get_agentic_rag() -> AgenticRAG:
    # Not cached: builds all four strategies fresh, same reason as above.
    return AgenticRAG()


def get_router() -> Router:
    return _get("router", Router)


def get_embedding_router() -> EmbeddingRouter:
    return _get("embedding_router", EmbeddingRouter)


def get_bandit() -> ContextualBandit:
    return _get("bandit", ContextualBandit)


def get_reward_tracker() -> RewardTracker:
    return _get("reward_tracker", RewardTracker)


def get_page_registry() -> PageRegistry:
    return _get("page_registry", PageRegistry)


def get_document_registry() -> DocumentRegistry:
    return _get("document_registry", DocumentRegistry)


def get_graph_registry() -> GraphRegistry:
    return _get("graph_registry", GraphRegistry)


def get_query_cache() -> QueryCache:
    return _get("query_cache", QueryCache)
