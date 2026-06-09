import json
import re

from src.llm.groq_client import (
    GroqLLM
)

from src.prompts.graph_extraction_prompt import (
    GRAPH_EXTRACTION_PROMPT
)


class EntityExtractor:

    def __init__(self):

        self.llm = GroqLLM()

    def extract(
        self,
        text: str
    ) -> dict:

        prompt = (
            GRAPH_EXTRACTION_PROMPT.format(
                text=text
            )
        )

        response = self.llm.invoke(
            prompt
        )

        try:

            json_match = re.search(
                r"\{.*\}",
                response,
                re.DOTALL
            )

            if json_match:

                return json.loads(
                    json_match.group()
                )

        except Exception:

            pass

        return {
            "entities": [],
            "relationships": []
        }