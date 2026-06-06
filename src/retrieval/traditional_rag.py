from typing import List

from langchain_core.documents import Document

from src.vectorstores.qdrant_store import QdrantStore
from src.llm.groq_client import GroqLLM
from src.prompts.rag_prompt import RAG_PROMPT


class TraditionalRAG:

    def __init__(self):

        self.store = QdrantStore()

        self.llm = GroqLLM()

    def retrieve(
        self,
        query: str,
        k: int = 5
    ) -> List[Document]:

        return self.store.similarity_search(
            query=query,
            k=k
        )

    def build_context(
        self,
        documents: List[Document]
    ) -> str:

        return "\n\n".join(
            doc.page_content
            for doc in documents
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

        return self.llm.invoke(prompt)

    def query(
        self,
        question: str,
        k: int = 5
    ) -> dict:

        retrieved_docs = self.retrieve(
            query=question,
            k=k
        )

        context = self.build_context(
            retrieved_docs
        )

        answer = self.generate_answer(
            question,
            context
        )

        return {
            "question": question,
            "answer": answer,
            "sources": retrieved_docs
        }