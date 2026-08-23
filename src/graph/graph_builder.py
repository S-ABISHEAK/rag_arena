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

        self.registry = (
            GraphRegistry()
        )

        self.graph_store = (
            self.registry.load_graph()
            or GraphStore()
        )

    def build(
        self,
        documents: list[Document]
    ) -> GraphStore:

        extraction_results = (
            self.extractor.extract_batch(
                [
                    document.page_content
                    for document in documents
                ]
            )
        )

        for extraction_result in extraction_results:

            self.graph_store.add_extraction_result(
                extraction_result
            )

        self.registry.save_graph(
            self.graph_store
        )

        return self.graph_store