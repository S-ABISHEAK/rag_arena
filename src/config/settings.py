from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
     

    # LLM
    
     
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # qwen/qwen3.8-27b: ~131k context window, same free-tier rate limits as
    # openai/gpt-oss-20b (30 RPM / 1K RPD / 8K TPM / 200K TPD as of writing —
    # verify at console.groq.com/docs/rate-limits, Groq revises these).
    # The context window is effectively unlimited for this project's prompt
    # sizes; the real constraint is the per-minute/per-day token budget,
    # which is why every prompt-building step below is capped explicitly
    # rather than relying on the model's own window.
    DEFAULT_LLM_MODEL = (
        "qwen/qwen3.8-27b"
    )

    # This is a reasoning model (dual thinking/instruct modes). Hidden
    # chain-of-thought tokens count against the same tight token budget as
    # visible output, and none of this project's tasks — classification,
    # extraction, summarization, RAG answer generation — need elaborate
    # reasoning. "none" disables thinking mode; set to "low"/"medium"/"high"
    # only if answer quality genuinely needs it and the budget allows.
    REASONING_EFFORT = "none"

    # Ceiling on generated tokens per call — a safety cap against runaway
    # generation (a reasoning model rambling, or an unexpectedly verbose
    # answer), not a target length. Comfortably covers a full RAG answer,
    # a page summary, or a batch of extracted entities.
    MAX_OUTPUT_TOKENS = 1024

    # Ceiling on the *retrieved context* assembled into a RAG prompt, across
    # every strategy (Traditional/Hybrid/PageIndex/Graph). PageIndexRAG in
    # particular can pull every chunk from several whole pages — without a
    # cap, one query could consume most of a minute's token budget by
    # itself. ~4000 tokens leaves headroom for the prompt template, the
    # question, and MAX_OUTPUT_TOKENS of answer within the 8K TPM ceiling.
    MAX_CONTEXT_TOKENS = 4000

    # Ceiling on a single page's content when it's inserted into a
    # page-summary or entity-extraction *batch* prompt. Chunks are already
    # bounded by CHUNK_SIZE below, but a raw PDF page (used for page
    # summaries) has no such bound — one unusually dense page could
    # otherwise dominate a batch's token budget.
    MAX_BATCH_ITEM_TOKENS = 2000


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

    # Set for a managed instance (e.g. Qdrant Cloud), e.g.
    # "https://xxxx.aws.cloud.qdrant.io:6333" — takes priority over
    # QDRANT_HOST/PORT when present. Cloud instances also require an API key.
    QDRANT_URL = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

    QDRANT_COLLECTION = (
        "documents"
    )


    # REDIS


    REDIS_HOST = os.getenv(
        "REDIS_HOST",
        "localhost"
    )

    REDIS_PORT = int(
        os.getenv(
            "REDIS_PORT",
            6379
        )
    )

    # Set for a managed instance (e.g. Upstash), e.g.
    # "rediss://default:<password>@xxxx.upstash.io:6379" — takes priority
    # over REDIS_HOST/PORT when present. Managed Redis providers typically
    # require both auth and TLS (the "rediss://" scheme), which plain
    # host/port can't express.
    REDIS_URL = os.getenv("REDIS_URL", "")


    # DATA
     

    PDF_DIRECTORY = (
        BASE_DIR / "data" / "pdfs"
    )


    # RETRIEVAL


    TOP_K = 5


    # API


    # Comma-separated list of allowed frontend origins, e.g.
    # "https://myapp.com,https://www.myapp.com" — falls back to the local
    # dev server ports so nothing extra needs configuring for local use.
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5183,http://localhost:5173,"
            "http://127.0.0.1:5183,http://127.0.0.1:5173"
        ).split(",")
        if origin.strip()
    ]

    MAX_UPLOAD_SIZE_MB = int(
        os.getenv(
            "MAX_UPLOAD_SIZE_MB",
            25
        )
    )

    # Shared secret required (as an "X-API-Key" header) on every mutating or
    # LLM-calling route once deployed — without it, a public deployment lets
    # anyone wipe the index or burn through the Groq quota for free. Empty
    # by default so local dev needs no setup; main.py logs a startup warning
    # when it's unset so that's a deliberate choice, not an oversight left
    # in at deploy time. Note this is only a bot/abuse deterrent, not a real
    # secret: the frontend must send the same value, and anything shipped to
    # a browser (Vite bakes VITE_-prefixed vars into the public JS bundle)
    # is visible to anyone who inspects the page.
    API_KEY = os.getenv("API_KEY", "")


settings = Settings()