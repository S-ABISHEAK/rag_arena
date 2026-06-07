from pathlib import Path
import pickle

from langchain_core.documents import Document


class DocumentRegistry:

    def __init__(
        self,
        registry_path: str = "data/registry/chunks.pkl"
    ):

        self.registry_path = Path(
            registry_path
        )

        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_documents(
        self,
        documents: list[Document]
    ) -> None:

        with open(
            self.registry_path,
            "wb"
        ) as file:

            pickle.dump(
                documents,
                file
            )

    def load_documents(
        self
    ) -> list[Document]:

        if not self.registry_path.exists():

            return []

        with open(
            self.registry_path,
            "rb"
        ) as file:

            return pickle.load(
                file
            )

    def append_documents(
        self,
        documents: list[Document]
    ) -> None:

        existing = self.load_documents()

        existing.extend(
            documents
        )

        self.save_documents(
            existing
        )

    def clear(self) -> None:

        if self.registry_path.exists():

            self.registry_path.unlink()


    def get_chunks_by_ids(
        self,
        chunk_ids: list[str]
    ):

        documents = self.load_documents()

        return [
            doc
            for doc in documents
            if doc.metadata.get(
                "chunk_id"
            ) in chunk_ids
        ]         