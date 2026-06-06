from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader


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

    loader = PyPDFLoader(str(path))
    documents = loader.load()

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
        loader = PyPDFLoader(str(pdf_file))
        documents.extend(loader.load())

    return documents