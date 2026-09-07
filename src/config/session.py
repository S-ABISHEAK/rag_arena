# Lightweight, no-login multi-tenancy: every browser gets a random
# anonymous ID (frontend generates it, sends it as the X-Session-Id
# header — see src/api/main.py's session_middleware and
# frontend/src/lib/api.ts). Everything that used to be one shared,
# global index/history is namespaced by that ID instead, so what one
# visitor uploads or queries is no longer visible to anyone else.
#
# A contextvars.ContextVar (not a plain global) is required here, not
# optional — FastAPI/Starlette handle concurrent requests as separate
# async tasks, and a plain global would let one request's session ID
# leak into a different, concurrently-running request. Starlette copies
# the current context when it dispatches a sync `def` route handler to
# its threadpool, so this is safe across both sync and async endpoints.

import contextvars
import re
from pathlib import Path

from src.config.settings import settings, BASE_DIR

_session_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "session_id", default=None
)

# Used only outside an actual HTTP request (CLI scripts, tests) where
# there's no browser session to isolate — preserves this project's
# original single-shared-index behavior for those cases.
_NO_REQUEST_FALLBACK = "default"

# The session ID becomes part of a filesystem path and a Qdrant collection
# name — it arrives as a client-supplied header, so it must be sanitized
# before either use, or a crafted value (e.g. "../../etc") could attempt
# path traversal. Restrict to a safe, generous charset and length.
_SAFE_SESSION_ID = re.compile(r"[^A-Za-z0-9_-]")
_MAX_SESSION_ID_LENGTH = 128


def _sanitize(session_id: str) -> str:
    cleaned = _SAFE_SESSION_ID.sub("", session_id)[:_MAX_SESSION_ID_LENGTH]
    return cleaned or _NO_REQUEST_FALLBACK


def set_session_id(session_id: str) -> None:
    _session_id.set(_sanitize(session_id))


def get_session_id() -> str:
    return _session_id.get() or _NO_REQUEST_FALLBACK


def session_data_dir() -> Path:
    return BASE_DIR / "data" / "sessions" / get_session_id()


def session_collection_name() -> str:
    return f"{settings.QDRANT_COLLECTION}_{get_session_id()}"
