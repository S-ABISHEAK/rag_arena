from langchain_groq import ChatGroq

from src.config.settings import settings


class GroqLLM:

    def __init__(
        self,
        model_name: str = settings.DEFAULT_LLM_MODEL,
        temperature: float = 0.0
    ):

        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=model_name,
            temperature=temperature
        )

    def invoke(
        self,
        prompt: str
    ) -> str:

        response = self.llm.invoke(prompt)

        return response.content