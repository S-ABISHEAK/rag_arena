import re

from src.config.settings import (
    settings
)
from src.pageindex.page_registry import (
    PageRegistry
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

    MAX_PAGE_CONTENT_CHARS = 1200

    def __init__(self):

        self.registry = PageRegistry()

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

    def build_context(
        self,
        selected_pages: list[int]
    ) -> str:

        context_parts = []

        for page in self.pages:

            if (
                page["page_number"]
                in selected_pages
            ):

                page_content = page["page_content"]

                if len(page_content) > self.MAX_PAGE_CONTENT_CHARS:

                    page_content = (
                        page_content[: self.MAX_PAGE_CONTENT_CHARS]
                        + "..."
                    )

                context_parts.append(
                    f"Page {page['page_number']}:\n{page_content}"
                )

        return "\n\n".join(
            context_parts
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

        context = (
            self.build_context(
                selected_pages
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
            "retrieval_type": (
                "pageindex"
            )
        }