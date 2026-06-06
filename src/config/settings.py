from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
     

    # LLM
    
     
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    DEFAULT_LLM_MODEL = (
        "llama-3.3-70b-versatile"
    )
     

    # EMBEDDINGS
  

    EMBEDDING_MODEL = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    EMBEDDING_DIMENSION = 384

     
    # CHUNKING
     

    CHUNK_SIZE = 1000

    CHUNK_OVERLAP = 200

     
    # QDRANT
     

    QDRANT_HOST = os.getenv(
        "QDRANT_HOST",
        "localhost"
    )

    QDRANT_PORT = int(
        os.getenv(
            "QDRANT_PORT",
            6333
        )
    )

    QDRANT_COLLECTION = (
        "documents"
    )

     
    # DATA
     

    PDF_DIRECTORY = (
        BASE_DIR / "data" / "pdfs"
    )

     
    # RETRIEVAL


    TOP_K = 5


settings = Settings()