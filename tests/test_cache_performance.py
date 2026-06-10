import time

from src.agents.agentic_rag import (
    AgenticRAG
)

rag = AgenticRAG()

question = (
    "What is Machine Learning?"
)

start = time.perf_counter()

response = rag.query(
    question
)

end = time.perf_counter()

print()

print(
    "Cache Hit:",
    response["cache_hit"]
)

print(
    "Latency:",
    round(
        end - start,
        4
    ),
    "seconds"
)