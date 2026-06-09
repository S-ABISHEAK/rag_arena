import networkx as nx


class GraphStore:

    def __init__(self):

        self.graph = nx.MultiDiGraph()

    def add_entity(
        self,
        entity: str
    ):

        self.graph.add_node(
            entity
        )

    def add_relationship(
        self,
        source: str,
        relation: str,
        target: str
    ):

        self.graph.add_edge(
            source,
            target,
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

        if entity not in self.graph:

            return []

        return list(
            self.graph.neighbors(
                entity
            )
        )

    def get_all_nodes(
        self
    ):

        return list(
            self.graph.nodes()
        )

    def get_all_edges(
        self
    ):

        return list(
            self.graph.edges(
                data=True
            )
        )

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

        if entity not in self.graph:

            return []

        relationships = []

        for source, target, data in self.graph.edges(
            entity,
            data=True
        ):

            relationships.append(
                {
                    "source": source,
                    "relation": data.get(
                        "relation",
                        ""
                    ),
                    "target": target
                }
            )

        return relationships
    
    def get_two_hop_subgraph(
    self,
    entity: str
    ):

        relationships = []

        if entity not in self.graph:

            return relationships

        for neighbor in self.graph.neighbors(
            entity
        ):

            relationships.extend(
                self.get_subgraph(
                    neighbor
                )
            )

        return relationships