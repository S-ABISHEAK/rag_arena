import json
import re

from src.llm.groq_client import (
    GroqLLM
)

from src.prompts.graph_extraction_prompt import (
    GRAPH_EXTRACTION_PROMPT,
    GRAPH_EXTRACTION_BATCH_PROMPT,
)

from src.utils.content_cache import ContentCache
from src.config.settings import settings
from src.utils.token_budget import truncate_to_token_budget

MIN_MEANINGFUL_CHARS = 40
BATCH_SIZE = 5


def _empty_result() -> dict:
    return {
        "entities": [],
        "relationships": []
    }


class EntityExtractor:

    def __init__(self):

        self.llm = GroqLLM()
        self.cache = ContentCache("data/llm_cache/entity_extractions.json")

    def extract(
        self,
        text: str
    ) -> dict:

        cached = self.cache.get(text)
        if cached is not None:
            return cached

        if len(text.strip()) < MIN_MEANINGFUL_CHARS:
            result = _empty_result()
            self.cache.set(text, result)
            return result

        prompt = (
            GRAPH_EXTRACTION_PROMPT.format(
                text=truncate_to_token_budget(
                    text, settings.MAX_BATCH_ITEM_TOKENS
                )
            )
        )

        response = self.llm.invoke(
            prompt
        )

        result = self._parse_single(response)
        self.cache.set(text, result)
        return result

    def extract_query(
        self,
        question: str
    ) -> dict:
        """
        Entity extraction for a live user question — deliberately separate
        from extract(): MIN_MEANINGFUL_CHARS exists to skip trivial/
        boilerplate document chunks while building the graph, but most real
        questions ("What is DNA?" is 12 characters) are shorter than that
        threshold. Reusing extract() here was silently discarding entities
        for nearly every question, so graph retrieval came back empty.
        Also intentionally not cached — a question is one-off, and caching
        it would let a single bad/truncated response permanently poison
        every future retry of that exact question.
        """

        if not question.strip():
            return _empty_result()

        prompt = (
            GRAPH_EXTRACTION_PROMPT.format(
                text=truncate_to_token_budget(
                    question, settings.MAX_BATCH_ITEM_TOKENS
                )
            )
        )

        response = self.llm.invoke(prompt)

        return self._parse_single(response)

    def extract_batch(
        self,
        texts: list[str]
    ) -> list[dict]:
        """
        Extract entities/relationships for multiple chunks using as few LLM
        calls as possible: already-cached and trivially-short chunks never
        touch the LLM, and everything else is grouped into BATCH_SIZE-chunk
        requests instead of one call per chunk.
        """

        results: list[dict | None] = [None] * len(texts)
        pending_indices: list[int] = []

        for i, text in enumerate(texts):

            cached = self.cache.get(text)

            if cached is not None:
                results[i] = cached
            elif len(text.strip()) < MIN_MEANINGFUL_CHARS:
                result = _empty_result()
                self.cache.set(text, result)
                results[i] = result
            else:
                pending_indices.append(i)

        for start in range(0, len(pending_indices), BATCH_SIZE):
            batch_indices = pending_indices[start:start + BATCH_SIZE]
            self._extract_batch_group(texts, batch_indices, results)

        return [r if r is not None else _empty_result() for r in results]

    def _extract_batch_group(
        self,
        texts: list[str],
        batch_indices: list[int],
        results: list[dict | None],
    ) -> None:

        chunks_block = "\n\n".join(
            f"--- Chunk index {i} ---\n"
            f"{truncate_to_token_budget(texts[i], settings.MAX_BATCH_ITEM_TOKENS)}"
            for i in batch_indices
        )

        prompt = GRAPH_EXTRACTION_BATCH_PROMPT.format(
            chunks_block=chunks_block
        )

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

                if idx not in batch_indices:
                    continue

                result = {
                    "entities": item.get("entities", []),
                    "relationships": item.get("relationships", []),
                }

                results[idx] = result
                self.cache.set(texts[idx], result)
                seen.add(idx)

            missing = [i for i in batch_indices if i not in seen]

        except Exception:
            missing = batch_indices

        # Fall back to an individual call only for whatever the batch
        # response didn't cleanly cover — never silently drop a chunk.
        for idx in missing:
            results[idx] = self.extract(texts[idx])

    @staticmethod
    def _parse_single(response: str) -> dict:

        try:
            json_match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if json_match:
                return json.loads(json_match.group())

        except Exception:
            pass

        return _empty_result()
