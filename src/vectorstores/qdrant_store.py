from typing import List

from langchain_core.documents import Document

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams
)

from langchain_qdrant import QdrantVectorStore

from src.config.settings import settings
from src.embeddings.embedder import (
    EmbeddingService
)

class QdrantStore:

    def __init__(self):

        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )

        self.embedding_service = (
            EmbeddingService()
        )

        self._create_collection()

        self.vectorstore = (
            QdrantVectorStore(
                client=self.client,
                collection_name=(
                    settings.QDRANT_COLLECTION
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
            settings.QDRANT_COLLECTION
            not in existing
        ):

            self.client.create_collection(
                collection_name=(
                    settings.QDRANT_COLLECTION
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
            collection_name=settings.QDRANT_COLLECTION
        )

        self._create_collection()    


    def collection_info(self):

        return self.client.get_collection(
            settings.QDRANT_COLLECTION
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