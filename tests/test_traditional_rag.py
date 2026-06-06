from src.retrieval.traditional_rag import (
    TraditionalRAG
)


rag = TraditionalRAG()

response = rag.query(
    "What is this document about?"
)

print()

print(
    "QUESTION:",
    response["question"]
)

print()

print(
    "ANSWER:",
    response["answer"]
)

print()

for doc in response["sources"]:

    print(doc.metadata)