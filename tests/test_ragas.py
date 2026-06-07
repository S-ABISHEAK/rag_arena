from src.retrieval.traditional_rag import (
    TraditionalRAG
)

from src.evaluation.ragas_evaluator import (
    RagasEvaluator
)


def test_ragas():

    rag = TraditionalRAG()

    response = rag.query(
        "What is AI-enabled security analytics?"
    )

    contexts = [
        doc.page_content
        for doc in response["sources"]
    ]

    result = (
        RagasEvaluator.evaluate_response(
            question=response["question"],
            answer=response["answer"],
            context=contexts
        )
    )

    print(result)

    assert result is not None