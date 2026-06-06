from src.ingestion.pdf_loader import (
    load_pdf
)

from src.chunking.text_splitter import (
    split_documents
)

from src.vectorstores.qdrant_store import (
    QdrantStore
)


docs = load_pdf(
    "data/pdfs/sample.pdf"
)

chunks = split_documents(
    docs
)

store = QdrantStore()

store.add_documents(
    chunks
)

results = store.similarity_search(
    "What is this document about?"
)

for doc in results:
    print(doc.metadata)
    print(doc.page_content[:300])
    print("-" * 50)