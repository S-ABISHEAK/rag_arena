import re
import threading
import time

from langchain_groq import ChatGroq

from src.config.settings import settings

# Groq's rate limit is account-wide, not per-connection, so every GroqLLM
# instance in this process shares one semaphore. Without it, concurrent
# requests (indexing + querying + benchmarking at once) each fire their own
# call and stack their token usage into the same one-minute window.
_groq_semaphore = threading.Semaphore(1)

_RETRY_AFTER_PATTERN = re.compile(r"try again in ([\d.]+)s", re.IGNORECASE)
MAX_RETRIES = 3


def _rate_limit_wait_seconds(exc: Exception) -> float | None:
    message = str(exc)

    if "rate_limit" not in message.lower() and "429" not in message:
        return None

    match = _RETRY_AFTER_PATTERN.search(message)
    if match:
        return float(match.group(1)) + 0.5

    return 5.0


class GroqLLM:

    def __init__(
        self,
        model_name: str = settings.DEFAULT_LLM_MODEL,
        temperature: float = 0.0,
        max_tokens: int = settings.MAX_OUTPUT_TOKENS,
        reasoning_effort: str = settings.REASONING_EFFORT
    ):

        self.llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            reasoning_effort=reasoning_effort
        )

    def invoke(
        self,
        prompt: str
    ) -> str:

        attempt = 0

        while True:
            try:
                with _groq_semaphore:
                    response = self.llm.invoke(prompt)

                return response.content

            except Exception as exc:
                wait_seconds = _rate_limit_wait_seconds(exc)

                if wait_seconds is None or attempt >= MAX_RETRIES:
                    raise

                attempt += 1
                time.sleep(wait_seconds)
