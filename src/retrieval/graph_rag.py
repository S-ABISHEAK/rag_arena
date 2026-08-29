from src.graph.graph_retriever import (
    GraphRetriever
)

from src.llm.groq_client import (
    GroqLLM
)

from src.prompts.rag_prompt import (
    RAG_PROMPT
)

from src.config.settings import (
    settings
)

from src.utils.token_budget import (
    truncate_to_token_budget
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

        context = (
            self.retriever.retrieve(
                question
            )
        )

        # A question that expands into many entities/relationships (e.g.
        # a densely-connected 2-hop neighborhood) could otherwise produce
        # an unbounded amount of relationship text.
        return truncate_to_token_budget(
            context,
            settings.MAX_CONTEXT_TOKENS
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