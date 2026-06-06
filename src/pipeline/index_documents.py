from pathlib import Path

from src.ingestion.pdf_loader import (
    load_pdf_directory
)

from src.chunking.text_splitter import (
    split_documents
)

from src.vectorstores.qdrant_store import (
    QdrantStore
)

from src.config.settings import (
    settings
)


class DocumentIndexer:

    def __init__(self):

        self.store = QdrantStore()

    def index_directory(
        self,
        directory_path: str | None = None
    ) -> int:

        directory = (
            directory_path
            or str(settings.PDF_DIRECTORY)
        )

        documents = load_pdf_directory(
            directory
        )

        chunks = split_documents(
            documents,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        self.store.add_documents(
            chunks
        )

        return len(chunks)

    def index_single_pdf(
        self,
        pdf_path: str
    ) -> int:

        from src.ingestion.pdf_loader import (
            load_pdf
        )

        documents = load_pdf(pdf_path)

        chunks = split_documents(
            documents,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        self.store.add_documents(
            chunks
        )

        return len(chunks)