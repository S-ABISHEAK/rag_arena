from src.ingestion.pdf_loader import (
    load_pdf
)

from src.chunking.text_splitter import (
    split_documents
)

from src.pageindex.page_index_builder import (
    PageIndexBuilder
)


def test_page_index_builder():

    pages = load_pdf(
        "data/pdfs/sample.pdf"
    )

    chunks = split_documents(
        pages
    )

    builder = PageIndexBuilder()

    builder.build(
        page_documents=pages,
        chunks=chunks
    )

    assert True