from src.pipeline.index_documents import (
    DocumentIndexer
)

from src.retrieval.traditional_rag import (
    TraditionalRAG
)


def main():

    indexer = DocumentIndexer()

    indexed_chunks = (
        indexer.index_directory()
    )

    print(
        f"Indexed {indexed_chunks} chunks"
    )

    rag = TraditionalRAG()

    while True:

        question = input(
            "\nQuestion (q to quit): "
        )

        if question.lower() == "q":
            break

        response = rag.query(question)

        print("\nAnswer:\n")
        print(response["answer"])


if __name__ == "__main__":
    main()