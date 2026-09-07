from typing import List

from langchain_core.documents import Document

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)

from langchain_qdrant import QdrantVectorStore

from src.config.settings import settings

def _build_qdrant_client() -> QdrantClient:
    # A managed instance (Qdrant Cloud) is reached over HTTPS with an API
    # key, which host/port alone can't express — QDRANT_URL takes priority
    # when set, otherwise fall back to the local host:port form.
    if settings.QDRANT_URL:
        return QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None
        )
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )


class QdrantStore:

    def __init__(self, collection_name: str | None = None):

        # Deferred: importing this module (e.g. for _build_qdrant_client,
        # used by the /health check) must never pull in
        # torch/transformers/sentence-transformers — only actually
        # constructing a QdrantStore should.
        from src.embeddings.embedder import EmbeddingService

        # Defaults to the current request's session (see
        # src/config/session.py) so each anonymous session gets its own
        # Qdrant collection instead of sharing one global index with every
        # other visitor to the site.
        from src.config.session import session_collection_name
        self.collection_name = collection_name or session_collection_name()

        self.client = _build_qdrant_client()

        self.embedding_service = (
            EmbeddingService()
        )

        self._create_collection()

        self.vectorstore = (
            QdrantVectorStore(
                client=self.client,
                collection_name=(
                    self.collection_name
                ),
                embedding=(
                    self.embedding_service.model
                )
            )
        )

    def _create_collection(self):

        collections = (
            self.client.get_collections()
        )

        existing = [
            c.name
            for c in collections.collections
        ]

        if (
            self.collection_name
            not in existing
        ):

            self.client.create_collection(
                collection_name=(
                    self.collection_name
                ),
                vectors_config=VectorParams(
                    size=(
                        settings
                        .EMBEDDING_DIMENSION
                    ),
                    distance=Distance.COSINE
                )
            )


    def add_documents(
        self,
        documents: List[Document]
    ):

        self.vectorstore.add_documents(
            documents
        )        

    
    def similarity_search(
        self,
        query: str,
        k: int = None
    ) -> List[Document]:

        if k is None:
            k = settings.TOP_K

        return (
            self.vectorstore
            .similarity_search(
                query=query,
                k=k
            )
        )     


    def as_retriever(
        self,
        k: int = None
    ):

        if k is None:
            k = settings.TOP_K

        return (
            self.vectorstore
            .as_retriever(
                search_kwargs={
                    "k": k
                }
            )
        )
    

    def delete_collection(self):

        self.client.delete_collection(
            collection_name=self.collection_name
        )

        self._create_collection()


    def collection_info(self):

        return self.client.get_collection(
            self.collection_name
        )
    

    def similarity_search_by_metadata(
    self,
    query: str,
    metadata_filter,
    k: int = 5
):
     return self.vectorstore.similarity_search(
        query=query,
        k=k,
        filter=metadata_filter
    )


    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5
    ):
        return self.vectorstore.similarity_search_with_score(
            query=query,
            k=k
        ) 