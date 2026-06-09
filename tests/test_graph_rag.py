from src.retrieval.graph_rag import (
    GraphRAG
)


rag = GraphRAG()

response = rag.query(
    "What is Machine Learning?"
)

print()

print(
    "Context:"
)

print(
    response["context"]
)

print()

print(
    "Answer:"
)

print(
    response["answer"]
)