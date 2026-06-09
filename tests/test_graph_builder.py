from src.storage.document_registry import (
    DocumentRegistry
)

from src.graph.graph_builder import (
    GraphBuilder
)


registry = DocumentRegistry()

documents = (
    registry.load_documents()
)

builder = GraphBuilder()

graph = builder.build(
    documents[:5]
)

print()

print(
    "Nodes:",
    graph.node_count()
)

print()

print(
    "Edges:",
    graph.edge_count()
)

print()

print(
    graph.get_all_nodes()[:20]
)

print()

print(
    graph.get_all_edges()[:20]
)