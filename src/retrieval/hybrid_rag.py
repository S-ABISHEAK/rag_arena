from typing import List

from langchain_core.documents import Document

from src.retrieval.traditional_rag import TraditionalRAG
from src.search.bm25_search import BM25Search
from src.storage.document_registry import (
    DocumentRegistry
)


class HybridRAG(TraditionalRAG):
    """
    Hybrid Retrieval Pipeline

    Retrieval Sources:
    - BM25 Lexical Search
    - Qdrant Dense Vector Search

    Retrieval Flow:
    Query
        ↓
    BM25 Search
        +
    Vector Search
        ↓
    Fusion
        ↓
    Context Construction
        ↓
    LLM Generation
    """

    def __init__(self):

        super().__init__()

        self.registry = DocumentRegistry()

        self.documents = (
            self.registry.load_documents()
        )

        if not self.documents:

            raise ValueError(
                "No indexed documents found. "
                "Run DocumentIndexer first."
            )

        self.bm25 = BM25Search(
            self.documents
        )

    def _deduplicate_documents(
        self,
        documents: List[Document]
    ) -> List[Document]:
        """
        Remove duplicate chunks while
        preserving retrieval order.
        """

        unique_documents = []

        seen = set()

        for doc in documents:

            source = doc.metadata.get(
                "source",
                ""
            )

            page = doc.metadata.get(
                "page",
                -1
            )

            chunk_id = doc.metadata.get(
                "chunk_id",
                ""
            )

            unique_key = (
                source,
                page,
                chunk_id
            )

            if unique_key not in seen:

                seen.add(
                    unique_key
                )

                unique_documents.append(
                    doc
                )

        return unique_documents

    def fuse_results(
        self,
        bm25_documents: List[Document],
        vector_documents: List[Document]
    ) -> List[Document]:
        """
        Merge lexical and semantic
        retrieval results.
        """

        merged_documents = (
            bm25_documents +
            vector_documents
        )

        return self._deduplicate_documents(
            merged_documents
        )

    def retrieve(
        self,
        query: str,
        k: int = 5
    ) -> List[Document]:
        """
        Hybrid retrieval using:

        1. BM25 Search
        2. Vector Search
        3. Result Fusion
        """

        bm25_documents = (
            self.bm25.search(
                query=query,
                k=k
            )
        )

        vector_documents = (
            self.store.similarity_search(
                query=query,
                k=k
            )
        )

        fused_documents = (
            self.fuse_results(
                bm25_documents,
                vector_documents
            )
        )

        return fused_documents[:k]

    def query(
        self,
        question: str,
        k: int = 5
    ) -> dict:
        """
        Execute complete
        Hybrid RAG pipeline.
        """

        retrieved_documents = (
            self.retrieve(
                query=question,
                k=k
            )
        )

        context = (
            self.build_context(
                retrieved_documents
            )
        )

        answer = (
            self.generate_answer(
                question=question,
                context=context
            )
        )

        return {
            "question": question,
            "answer": answer,
            "sources": retrieved_documents,
            "retrieval_type": "hybrid",
            "retrieved_chunks": len(
                retrieved_documents
            )
        }