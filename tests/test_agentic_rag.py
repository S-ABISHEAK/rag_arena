from src.agents.agentic_rag import (
    AgenticRAG
)

agent = AgenticRAG()

response = agent.query(
    "Summarize the document."
)

print()

print(
    "Strategy:"
)

print(
    response["selected_strategy"]
)

print()

print(
    "Answer:"
)

print(
    response["answer"]
)