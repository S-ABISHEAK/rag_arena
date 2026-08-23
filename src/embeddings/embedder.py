from typing import List

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config.settings import settings


class EmbeddingService:

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL
    ):

        self.model = HuggingFaceEmbeddings(
            model_name=model_name
        )

    def embed_documents(
        self,
        documents: List[Document]
    ) -> List[List[float]]:
        """
        Generate embeddings for document chunks.
        """

        texts = [
            doc.page_content
            for doc in documents
        ]

        return self.model.embed_documents(texts)

    def embed_query(
        self,
        query: str
    ) -> List[float]:
        """
        Generate embedding for user query.
        """

        return self.model.embed_query(query)