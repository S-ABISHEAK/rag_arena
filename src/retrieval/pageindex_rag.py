import re

from langchain_core.documents import Document

from src.config.settings import (
    settings
)

from src.pageindex.page_registry import (
    PageRegistry
)

from src.storage.document_registry import (
    DocumentRegistry
)

from src.llm.groq_client import (
    GroqLLM
)

from src.prompts.page_selection_prompt import (
    PAGE_SELECTION_PROMPT
)

from src.prompts.rag_prompt import (
    RAG_PROMPT
)


class PageIndexRAG:

    MAX_SELECTED_PAGES = settings.TOP_K

    def __init__(self):

        self.registry = PageRegistry()

        self.document_registry = (
            DocumentRegistry()
        )

        self.llm = GroqLLM()

        self.pages = (
            self.registry.get_all_pages()
        )

        if not self.pages:

            raise ValueError(
                "No PageIndex found. "
                "Run DocumentIndexer first."
            )

    def select_pages(
        self,
        question: str
    ) -> list[int]:

        page_descriptions = []

        for page in self.pages:

            page_descriptions.append(
                f"""
Page Number:
{page["page_number"]}

Summary:
{page["summary"]}
"""
            )

        pages_text = "\n".join(
            page_descriptions
        )

        prompt = (
            PAGE_SELECTION_PROMPT.format(
                question=question,
                pages=pages_text
            )
        )

        response = self.llm.invoke(
            prompt
        )

        page_numbers = re.findall(
            r"\d+",
            response
        )

        valid_pages = {
            page["page_number"]
            for page in self.pages
        }

        unique_pages = []

        seen_pages = set()

        for page_number in page_numbers:

            page = int(page_number)

            if (
                page in valid_pages
                and page not in seen_pages
            ):

                seen_pages.add(page)

                unique_pages.append(page)

        return unique_pages[
            : self.MAX_SELECTED_PAGES
        ]

    def get_chunks_from_pages(
        self,
        selected_pages: list[int]
    ) -> list[Document]:

        selected_chunk_ids = []

        for page in self.pages:

            if (
                page["page_number"]
                in selected_pages
            ):

                selected_chunk_ids.extend(
                    page["chunk_ids"]
                )

        return (
            self.document_registry
            .get_chunks_by_ids(
                selected_chunk_ids
            )
        )

    def build_context(
        self,
        chunks: list[Document]
    ) -> str:

        return "\n\n".join(
            chunk.page_content
            for chunk in chunks
        )

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        prompt = RAG_PROMPT.format(
            context=context,
            question=question
        )

        return self.llm.invoke(
            prompt
        )

    def query(
        self,
        question: str
    ) -> dict:

        selected_pages = (
            self.select_pages(
                question
            )
        )

        chunks = (
            self.get_chunks_from_pages(
                selected_pages
            )
        )

        context = (
            self.build_context(
                chunks
            )
        )

        answer = (
            self.generate_answer(
                question,
                context
            )
        )

        return {
            "question": question,
            "answer": answer,
            "selected_pages": (
                selected_pages
            ),
            "retrieved_chunks": (
                len(chunks)
            ),
            "retrieval_type": (
                "pageindex_v2"
            )
        }