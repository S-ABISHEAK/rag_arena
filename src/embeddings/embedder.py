import threading
from typing import List

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config.settings import settings

# HybridRAG/PageIndexRAG/GraphRAG are deliberately reconstructed fresh on
# every request (see src/api/resources.py) so they never serve stale data
# after a re-index. But that meant every request also re-loaded the
# embedding model's weights from disk — the model itself never changes,
# only the document/page/graph data does. Cache the loaded model by name at
# module level so it's loaded once per process; each EmbeddingService still
# gets constructed fresh (cheap), it just reuses the underlying model.
_model_cache: dict[str, HuggingFaceEmbeddings] = {}
_model_cache_lock = threading.Lock()


def _get_model(model_name: str) -> HuggingFaceEmbeddings:
    if model_name not in _model_cache:
        with _model_cache_lock:
            if model_name not in _model_cache:
                _model_cache[model_name] = HuggingFaceEmbeddings(model_name=model_name)
    return _model_cache[model_name]


class EmbeddingService:

    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL
    ):

        self.model = _get_model(model_name)

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
