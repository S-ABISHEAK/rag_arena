from src.llm.groq_client import (
    GroqLLM
)


PAGE_SUMMARY_PROMPT = """
You are building a PageIndex system.

Create a concise retrieval summary for the page.

Requirements:
- Maximum 3 sentences
- Mention important topics
- Mention important entities
- Mention key concepts
- Do not include unnecessary details

Page Content:

{page_content}

Summary:
"""


class PageSummaryBuilder:

    def __init__(self):

        self.llm = GroqLLM()

    def generate_summary(
        self,
        page_content: str
    ) -> str:

        prompt = PAGE_SUMMARY_PROMPT.format(
            page_content=page_content
        )

        return self.llm.invoke(
            prompt
        ).strip()