import time

from src.evaluation.metrics import (
    Metrics
)

from src.evaluation.evaluation_result import (
    EvaluationResult
)

def benchmark_rag(
    rag,
    rag_name: str,
    question: str
):

    start_time = time.time()

    response = rag.query(
        question
    )

    end_time = time.time()

    return EvaluationResult(
        rag_name=rag_name,
        question=question,
        answer=response["answer"],
        latency=Metrics.measure_latency(
            start_time,
            end_time
        ),
        retrieved_chunks=len(
            response["sources"]
        )
    )


def compare_rags(
    question: str,
    traditional_rag,
    hybrid_rag
):

    traditional_result = (
        benchmark_rag(
            traditional_rag,
            "Traditional RAG",
            question
        )
    )

    hybrid_result = (
        benchmark_rag(
            hybrid_rag,
            "Hybrid RAG",
            question
        )
    )

    return [
        traditional_result,
        hybrid_result
    ]