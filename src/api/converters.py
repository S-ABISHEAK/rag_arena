from langchain_core.documents import Document

from src.api.schemas import QueryResult, Source

SNIPPET_LENGTH = 300


def document_to_source(doc: Document) -> Source:
    return Source(
        source=doc.metadata.get("source", ""),
        page=doc.metadata.get("page", -1),
        chunk_id=doc.metadata.get("chunk_id"),
        snippet=doc.page_content[:SNIPPET_LENGTH],
    )


def build_query_result(
    raw: dict,
    retrieval_type: str,
    latency: float,
) -> QueryResult:
    sources = raw.get("sources")

    return QueryResult(
        question=raw["question"],
        answer=raw["answer"],
        retrieval_type=raw.get("retrieval_type", retrieval_type),
        selected_strategy=raw.get("selected_strategy"),
        latency=latency,
        cache_hit=raw.get("cache_hit", False),
        sources=[document_to_source(d) for d in sources] if sources else None,
        selected_pages=raw.get("selected_pages"),
        context=raw.get("context"),
    )
