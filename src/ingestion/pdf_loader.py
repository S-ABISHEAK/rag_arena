from pathlib import Path
from typing import List

from langchain_core.documents import Document
from pypdf import PdfReader


def load_pdf(pdf_path: str) -> List[Document]:
    """
    Load a single PDF and return LangChain Documents.

    Args:
        pdf_path: Absolute or relative path to PDF.

    Returns:
        List[Document]
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Unsupported file type: {path.suffix}")

    # Extract text using pypdf and wrap into LangChain Documents
    reader = PdfReader(path)
    documents: List[Document] = []
    
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        metadata = {"source": str(path), "page": page_num}
        documents.append(Document(page_content=text, metadata=metadata))

    return documents


def load_pdf_directory(directory_path: str) -> List[Document]:
    """
    Load all PDFs from a directory.

    Args:
        directory_path: Folder containing PDFs.

    Returns:
        Combined list of documents.
    """

    directory = Path(directory_path)

    if not directory.exists():
        raise FileNotFoundError(
            f"Directory not found: {directory_path}"
        )

    documents: List[Document] = []

    pdf_files = sorted(directory.glob("*.pdf"))

    for pdf_file in pdf_files:
        # Reuses the updated load_pdf function logic safely
        documents.extend(load_pdf(str(pdf_file)))

    return documents
