from src.retrieval.pageindex_rag import (
    PageIndexRAG
)


def test_pageindex_rag():

    rag = PageIndexRAG()

    response = rag.query(
        "What is AI-enabled security analytics?"
    )

    print()

    print(
        response["selected_pages"]
    )

    print()

    print(
        response["answer"]
    )

    assert response["answer"]