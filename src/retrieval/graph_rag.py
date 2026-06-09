from src.graph.graph_retriever import (
    GraphRetriever
)

from src.llm.groq_client import (
    GroqLLM
)

from src.prompts.rag_prompt import (
    RAG_PROMPT
)


class GraphRAG:

    def __init__(self):

        self.retriever = (
            GraphRetriever()
        )

        self.llm = GroqLLM()

    def build_context(
        self,
        question: str
    ) -> str:

        return (
            self.retriever.retrieve(
                question
            )
        )

    def generate_answer(
        self,
        question: str,
        context: str
    ) -> str:

        prompt = RAG_PROMPT.format(
            context=context,
            question=question
        )

        return self.llm.invoke(
            prompt
        )

    def query(
        self,
        question: str
    ) -> dict:

        context = (
            self.build_context(
                question
            )
        )

        answer = (
            self.generate_answer(
                question,
                context
            )
        )

        return {
            "question": question,
            "answer": answer,
            "context": context,
            "retrieval_type": "graph"
        }