import networkx as nx


class GraphStore:

    def __init__(self):

        self.graph = nx.MultiDiGraph()

    @staticmethod
    def _normalize(entity: str) -> str:
        # The LLM re-extracts entity names fresh for every chunk and for
        # every question, so the same real-world entity routinely comes
        # back as "Mitochondria", "mitochondria", or "the mitochondria".
        # Without normalizing, those become unrelated graph nodes and a
        # question's extracted entity almost never string-matches the node
        # created at build time — this is why retrieval kept coming back
        # empty. Node identity is the normalized key; the original casing
        # is kept as a display_name attribute for readable output.
        return " ".join(entity.strip().lower().split())

    def add_entity(
        self,
        entity: str
    ):

        key = self._normalize(entity)

        if not key:
            return

        if key not in self.graph:
            self.graph.add_node(key, display_name=entity.strip())

    def add_relationship(
        self,
        source: str,
        relation: str,
        target: str
    ):

        source_key = self._normalize(source)
        target_key = self._normalize(target)

        if not source_key or not target_key:
            return

        if source_key not in self.graph:
            self.graph.add_node(source_key, display_name=source.strip())

        if target_key not in self.graph:
            self.graph.add_node(target_key, display_name=target.strip())

        self.graph.add_edge(
            source_key,
            target_key,
            relation=relation
        )

    def add_extraction_result(
        self,
        extraction_result: dict
    ):

        entities = (
            extraction_result.get(
                "entities",
                []
            )
        )

        relationships = (
            extraction_result.get(
                "relationships",
                []
            )
        )

        for entity in entities:

            self.add_entity(
                entity
            )

        for relation in relationships:

            self.add_relationship(
                source=relation["source"],
                relation=relation["relation"],
                target=relation["target"]
            )

    def get_neighbors(
        self,
        entity: str
    ):

        key = self._normalize(entity)

        if key not in self.graph:

            return []

        return [
            self.graph.nodes[neighbor].get("display_name", neighbor)
            for neighbor in self.graph.neighbors(key)
        ]

    def get_all_nodes(
        self
    ):

        return [
            data.get("display_name", node)
            for node, data in self.graph.nodes(data=True)
        ]

    def get_all_edges(
        self
    ):

        return [
            (
                self.graph.nodes[source].get("display_name", source),
                self.graph.nodes[target].get("display_name", target),
                data,
            )
            for source, target, data in self.graph.edges(data=True)
        ]

    def node_count(
        self
    ):

        return self.graph.number_of_nodes()

    def edge_count(
        self
    ):

        return self.graph.number_of_edges()
    
    def get_subgraph(
    self,
    entity: str
    ):

        key = self._normalize(entity)

        if key not in self.graph:

            return []

        relationships = []

        for source, target, data in self.graph.edges(
            key,
            data=True
        ):

            relationships.append(
                {
                    "source": self.graph.nodes[source].get("display_name", source),
                    "relation": data.get(
                        "relation",
                        ""
                    ),
                    "target": self.graph.nodes[target].get("display_name", target)
                }
            )

        return relationships

    def get_two_hop_subgraph(
    self,
    entity: str
    ):

        relationships = []

        key = self._normalize(entity)

        if key not in self.graph:

            return relationships

        for neighbor in self.graph.neighbors(
            key
        ):

            relationships.extend(
                self.get_subgraph(
                    neighbor
                )
            )

        return relationships