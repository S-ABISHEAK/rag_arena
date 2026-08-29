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

    def build(
        self,
        documents: list[Document]
    ) -> GraphStore:

        # The slow part — LLM extraction — runs outside the lock so it
        # doesn't block other concurrent builds from reading/writing the
        # graph file while it's in flight.
        extraction_results = (
            self.extractor.extract_batch(
                [
                    document.page_content
                    for document in documents
                ]
            )
        )

        # Load, merge, and save as one atomic unit: without this lock, two
        # concurrent builds could both load the same base graph, each add
        # their own entities in memory, and whichever saves last would
        # silently discard the other's additions.
        with GraphRegistry._lock:

            graph_store = (
                self.registry.load_graph()
                or GraphStore()
            )

            for extraction_result in extraction_results:

                graph_store.add_extraction_result(
                    extraction_result
                )

            self.registry.save_graph(
                graph_store
            )

        return graph_store
