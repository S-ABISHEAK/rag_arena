from langchain_core.documents import Document

from src.pageindex.page_registry import (
    PageRegistry
)

from src.pageindex.page_summary_builder import (
    PageSummaryBuilder
)


class PageIndexBuilder:

    def __init__(self):

        self.registry = (
            PageRegistry()
        )

        self.summary_builder = (
            PageSummaryBuilder()
        )

    def build(
        self,
        page_documents: list[Document],
        chunks: list[Document]
    ) -> None:

        for page_doc in page_documents:

            source = page_doc.metadata.get(
                "source",
                ""
            )

            page_number = page_doc.metadata.get(
                "page",
                -1
            )

            page_content = (
                page_doc.page_content
            )

            summary = (
                self.summary_builder
                .generate_summary(
                    page_content
                )
            )

            chunk_ids = []

            for chunk in chunks:

                if (
                    chunk.metadata.get(
                        "source"
                    ) == source
                    and
                    chunk.metadata.get(
                        "page"
                    ) == page_number
                ):

                    chunk_ids.append(
                        chunk.metadata.get(
                            "chunk_id"
                        )
                    )

            self.registry.add_page(
                source=source,
                page_number=page_number,
                page_content=page_content,
                summary=summary,
                chunk_ids=chunk_ids
            )