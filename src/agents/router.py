from src.llm.groq_client import (
    GroqLLM
)

from src.prompts.router_prompt import (
    ROUTER_PROMPT
)


class Router:

    def __init__(self):

        self.llm = GroqLLM()

    def route(
        self,
        question: str
    ) -> str:

        prompt = (
            ROUTER_PROMPT.format(
                question=question
            )
        )

        response = (
            self.llm.invoke(
                prompt
            )
            .strip()
            .upper()
        )

        return response