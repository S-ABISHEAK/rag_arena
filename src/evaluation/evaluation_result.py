from dataclasses import dataclass


@dataclass
class EvaluationResult:

    rag_name: str

    question: str

    answer: str

    latency: float

    retrieved_chunks: int