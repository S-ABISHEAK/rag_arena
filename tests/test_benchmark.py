from src.retrieval.traditional_rag import (
    TraditionalRAG
)

from src.retrieval.hybrid_rag import (
    HybridRAG
)

from src.evaluation.benchmark import (
    compare_rags
)


def main():

    results = compare_rags(
        question="What is Redis?",
        traditional_rag=TraditionalRAG(),
        hybrid_rag=HybridRAG()
    )

    for result in results:

        print("\n" + "=" * 60)

        print(
            f"RAG Type: {result.rag_name}"
        )

        print(
            f"Latency: {result.latency}s"
        )

        print(
            f"Retrieved Chunks: "
            f"{result.retrieved_chunks}"
        )

        print("\nAnswer:\n")

        print(result.answer[:500])


if __name__ == "__main__":
    main()