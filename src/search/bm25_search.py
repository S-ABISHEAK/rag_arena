from rank_bm25 import BM25Okapi

from langchain_core.documents import Document


class BM25Search:

    def __init__(
        self,
        documents: list[Document]
    ):

        self.documents = documents

        self.tokenized_docs = [
            doc.page_content.split()
            for doc in documents
        ]

        self.bm25 = BM25Okapi(
            self.tokenized_docs
        )

    def search(
        self,
        query: str,
        k: int = 5
    ) -> list[Document]:

        tokenized_query = query.split()

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:k]

        return [
            self.documents[i]
            for i in ranked_indices
        ]