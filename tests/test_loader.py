from src.ingestion.pdf_loader import load_pdf

docs = load_pdf("data/pdfs/sample.pdf")

print(f"Pages Loaded: {len(docs)}")
print(docs[0].page_content[:500])
print(docs[0].metadata)