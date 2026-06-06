from src.ingestion.pdf_loader import (
    load_pdf,
    load_pdf_directory
)

from src.chunking.text_splitter import (
    split_documents
)

from src.vectorstores.qdrant_store import (
    QdrantStore
)

from src.storage.document_registry import (
    DocumentRegistry
)

from src.pageindex.page_registry import (
    PageRegistry
)

from src.pageindex.page_index_builder import (
    PageIndexBuilder
)

from src.config.settings import (
    settings
)


class DocumentIndexer:

    def __init__(self):

        self.store = QdrantStore()

        self.registry = DocumentRegistry()

        self.page_registry = PageRegistry()

        self.page_index_builder = (
            PageIndexBuilder()
        )

    def index_directory(
        self,
        directory_path: str | None = None,
        reset_registry: bool = False
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

        if reset_registry:

            self.registry.clear()

            self.page_registry.clear()

        self.store.add_documents(
            chunks
        )

        self.registry.append_documents(
            chunks
        )

        self.page_index_builder.build(
            page_documents=documents,
            chunks=chunks
        )

        return len(chunks)

    def index_single_pdf(
        self,
        pdf_path: str
    ) -> int:

        documents = load_pdf(
            pdf_path
        )

        chunks = split_documents(
            documents,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

        self.store.add_documents(
            chunks
        )

        self.registry.append_documents(
            chunks
        )

        self.page_index_builder.build(
            page_documents=documents,
            chunks=chunks
        )

        return len(chunks)

    def get_indexed_documents_count(
        self
    ) -> int:

        documents = (
            self.registry.load_documents()
        )

        return len(documents)

    def clear_registry(
        self
    ) -> None:

        self.registry.clear()

        self.page_registry.clear()