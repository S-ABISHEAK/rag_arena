from src.ingestion.pdf_loader import (
    load_pdf
)

from src.chunking.text_splitter import (
    split_documents
)

from src.retrieval.hybrid_rag import (
    HybridRAG
)


documents = load_pdf(
    "data/pdfs/sample.pdf"
)

chunks = split_documents(
    documents
)

rag = HybridRAG(
    all_documents=chunks
)

response = rag.query(
    "What is this document about?"
)

print("\nQuestion:")
print(response["question"])

print("\nAnswer:")
print(response["answer"])

print("\nSources:")

for doc in response["sources"]:
    print(doc.metadata)