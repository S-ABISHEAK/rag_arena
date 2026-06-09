from src.graph.graph_retriever import (
    GraphRetriever
)

retriever = GraphRetriever()

context = retriever.retrieve(
    "What is Machine Learning?"
)

print()

print(context)