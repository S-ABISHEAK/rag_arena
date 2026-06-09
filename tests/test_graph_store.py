from src.graph.graph_store import (
    GraphStore
)

graph = GraphStore()

graph.add_extraction_result(
    {
        "entities": [
            "Microsoft",
            "GitHub"
        ],
        "relationships": [
            {
                "source": "Microsoft",
                "relation": "owns",
                "target": "GitHub"
            }
        ]
    }
)

print()

print(
    graph.get_all_nodes()
)

print()

print(
    graph.get_all_edges()
)

print()

print(
    graph.get_neighbors(
        "Microsoft"
    )
)