from langchain_core.documents import (
    Document
)

from src.graph.entity_extractor import (
    EntityExtractor
)

from src.graph.graph_store import (
    GraphStore
)

from src.graph.graph_registry import (
    GraphRegistry
)

class GraphBuilder:

    def __init__(self):

        self.extractor = (
            EntityExtractor()
        )

        self.graph_store = (
            GraphStore()
        )

        self.registry = (
            GraphRegistry()
        )

    def build(
        self,
        documents: list[Document]
    ) -> GraphStore:

        for document in documents:

            extraction_result = (
                self.extractor.extract(
                    document.page_content
                )
            )

            self.graph_store.add_extraction_result(
                extraction_result
            )

            self.registry.save_graph(
                self.graph_store
            )

        return self.graph_store