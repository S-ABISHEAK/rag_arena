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

from src.utils.token_budget import (
    truncate_to_token_budget
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
        """
        Returns a list of Page IDs — indices into self.pages — NOT the
        document's own page number. Page numbers restart at 0 for every
        indexed PDF, so once more than one document is indexed they
        collide; the Page ID (this list's index) is the only value that
        stays unique across every indexed document.
        """

        page_descriptions = []

        for page_id, page in enumerate(self.pages):

            page_descriptions.append(
                f"""
Page ID:
{page_id}

Source:
{page["source"]}

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

        page_ids = re.findall(
            r"\d+",
            response
        )

        valid_page_ids = set(
            range(len(self.pages))
        )

        unique_page_ids = []

        seen_page_ids = set()

        for page_id in page_ids:

            page_id = int(page_id)

            if (
                page_id in valid_page_ids
                and page_id not in seen_page_ids
            ):

                seen_page_ids.add(page_id)

                unique_page_ids.append(page_id)

        return unique_page_ids[
            : self.MAX_SELECTED_PAGES
        ]

    def get_chunks_from_pages(
        self,
        selected_page_ids: list[int]
    ) -> list[Document]:

        selected_chunk_ids = []

        for page_id in selected_page_ids:

            selected_chunk_ids.extend(
                self.pages[page_id]["chunk_ids"]
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

        context = "\n\n".join(
            chunk.page_content
            for chunk in chunks
        )

        # Unlike Traditional/Hybrid, this can pull EVERY chunk from up to
        # MAX_SELECTED_PAGES whole pages — a handful of dense pages could
        # otherwise consume most of a minute's token budget in one query.
        return truncate_to_token_budget(
            context,
            settings.MAX_CONTEXT_TOKENS
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

        selected_page_ids = (
            self.select_pages(
                question
            )
        )

        chunks = (
            self.get_chunks_from_pages(
                selected_page_ids
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

        # "selected_pages" is reported as each source's own page number,
        # for display — the Page IDs above exist only to keep retrieval
        # correct when multiple documents are indexed.
        selected_pages = [
            self.pages[page_id]["page_number"]
            for page_id in selected_page_ids
        ]

        return {
            "question": question,
            "answer": answer,
            "selected_pages": (
                selected_pages
            ),
            "sources": chunks,
            "context": context,
            "retrieved_chunks": (
                len(chunks)
            ),
            "retrieval_type": (
                "pageindex_v2"
            )
        }