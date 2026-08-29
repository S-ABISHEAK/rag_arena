import json
import re

from src.llm.groq_client import (
    GroqLLM
)

from src.utils.content_cache import ContentCache
from src.config.settings import settings
from src.utils.token_budget import truncate_to_token_budget


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

PAGE_SUMMARY_BATCH_PROMPT = """
You are building a PageIndex system.

Create a concise retrieval summary for EACH of the following pages.

Requirements per summary:
- Maximum 3 sentences
- Mention important topics, entities, and key concepts
- Do not include unnecessary details

Return ONLY a JSON array, one object per page, in the same order given,
with no other text:
[{{"index": <page index>, "summary": "..."}}, ...]

Pages:

{pages_block}
"""

MIN_MEANINGFUL_CHARS = 40
BATCH_SIZE = 5
FALLBACK_SUMMARY = "(Page has minimal extractable text content.)"


class PageSummaryBuilder:

    def __init__(self):

        self.llm = GroqLLM()
        self.cache = ContentCache("data/llm_cache/page_summaries.json")

    def generate_summary(
        self,
        page_content: str
    ) -> str:

        cached = self.cache.get(page_content)
        if cached is not None:
            return cached

        if len(page_content.strip()) < MIN_MEANINGFUL_CHARS:
            self.cache.set(page_content, FALLBACK_SUMMARY)
            return FALLBACK_SUMMARY

        prompt = PAGE_SUMMARY_PROMPT.format(
            page_content=truncate_to_token_budget(
                page_content, settings.MAX_BATCH_ITEM_TOKENS
            )
        )

        summary = self.llm.invoke(prompt).strip()
        # Cached under the original (untruncated) content, so the cache
        # key reflects what the page actually is, not the truncated view
        # the LLM happened to see.
        self.cache.set(page_content, summary)
        return summary

    def generate_summaries_batch(
        self,
        pages: list[str]
    ) -> list[str]:
        """
        Summarize multiple pages using as few LLM calls as possible:
        already-cached and trivially-short pages never touch the LLM, and
        everything else is grouped into BATCH_SIZE-page requests instead of
        one call per page.
        """

        results: list[str | None] = [None] * len(pages)
        pending_indices: list[int] = []

        for i, content in enumerate(pages):

            cached = self.cache.get(content)

            if cached is not None:
                results[i] = cached
            elif len(content.strip()) < MIN_MEANINGFUL_CHARS:
                self.cache.set(content, FALLBACK_SUMMARY)
                results[i] = FALLBACK_SUMMARY
            else:
                pending_indices.append(i)

        for start in range(0, len(pending_indices), BATCH_SIZE):
            batch_indices = pending_indices[start:start + BATCH_SIZE]
            self._summarize_batch(pages, batch_indices, results)

        return [r if r is not None else FALLBACK_SUMMARY for r in results]

    def _summarize_batch(
        self,
        pages: list[str],
        batch_indices: list[int],
        results: list[str | None],
    ) -> None:

        pages_block = "\n\n".join(
            f"--- Page index {i} ---\n"
            f"{truncate_to_token_budget(pages[i], settings.MAX_BATCH_ITEM_TOKENS)}"
            for i in batch_indices
        )

        prompt = PAGE_SUMMARY_BATCH_PROMPT.format(pages_block=pages_block)

        try:
            response = self.llm.invoke(prompt)
            json_match = re.search(r"\[.*\]", response, re.DOTALL)
            parsed = json.loads(json_match.group()) if json_match else []

            seen = set()

            for item in parsed:
                try:
                    idx = int(item.get("index"))
                except (TypeError, ValueError):
                    continue

                summary = str(item.get("summary", "")).strip()

                if idx in batch_indices and summary:
                    results[idx] = summary
                    self.cache.set(pages[idx], summary)
                    seen.add(idx)

            missing = [i for i in batch_indices if i not in seen]

        except Exception:
            missing = batch_indices

        # Fall back to an individual call only for whatever the batch
        # response didn't cleanly cover — never silently drop a page.
        for idx in missing:
            results[idx] = self.generate_summary(pages[idx])
