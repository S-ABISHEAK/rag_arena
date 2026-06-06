from src.ingestion.pdf_loader import load_pdf
from src.chunking.text_splitter import split_documents
from src.embeddings.embedder import EmbeddingService


docs = load_pdf(
    "data/pdfs/sample.pdf"
)

chunks = split_documents(docs)

embedding_service = EmbeddingService()

vectors = embedding_service.embed_documents(
    chunks[:5]
)

print(
    f"Chunks: {len(chunks)}"
)

print(
    f"Embeddings: {len(vectors)}"
)

print(
    f"Dimension: {len(vectors[0])}"
)