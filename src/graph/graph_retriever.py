from src.graph.graph_registry import (
    GraphRegistry
)

from src.graph.entity_extractor import (
    EntityExtractor
)


class GraphRetriever:

    def __init__(self):

        self.registry = (
            GraphRegistry()
        )

        self.extractor = (
            EntityExtractor()
        )

        self.graph_store = (
            self.registry.load_graph()
        )

        if self.graph_store is None:

            raise ValueError(
                "Graph not found. "
                "Run GraphBuilder first."
            )

    def extract_query_entities(
        self,
        question: str
    ):

        result = (
            self.extractor.extract(
                question
            )
        )

        return result.get(
            "entities",
            []
        )

    def retrieve(
        self,
        question: str
    ) -> str:

        entities = (
            self.extract_query_entities(
                question
            )
        )

        context_parts = []

        for entity in entities:

            relationships = (
                self.graph_store
                .get_subgraph(entity)
            )

            relationships.extend(
                self.graph_store
                .get_two_hop_subgraph(
                    entity
                )
            )

            if not relationships:
                continue

            context_parts.append(
                f"\nEntity: {entity}"
            )

            for relationship in relationships:

                context_parts.append(
                    f"{relationship['source']} "
                    f"{relationship['relation']} "
                    f"{relationship['target']}"
                )

        return "\n".join(
            context_parts
        )