import datetime
import time

from qdrant_client import QdrantClient

from src.cache.redis_client import RedisClient
from src.config.settings import settings
from src.api.schemas import ConnectionHealth

# Qdrant/Redis checks are cheap local pings, but Groq's is a real API call
# against the same account the LLM calls use — polling it on every /health
# hit (e.g. every frontend poller, times however many mounted components)
# burns request quota for no reason. Cache its result for a short window.
_GROQ_HEALTH_TTL_SECONDS = 30
_groq_health_cache: dict = {"result": None, "expires_at": 0.0}


def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def check_qdrant() -> ConnectionHealth:
    try:
        client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        client.get_collections()
        return ConnectionHealth(service="Qdrant", connected=True, last_checked=_now())
    except Exception as exc:
        return ConnectionHealth(service="Qdrant", connected=False, last_checked=_now(), detail=str(exc))


def check_redis() -> ConnectionHealth:
    try:
        RedisClient.get_client().ping()
        return ConnectionHealth(service="Redis", connected=True, last_checked=_now())
    except Exception as exc:
        return ConnectionHealth(service="Redis", connected=False, last_checked=_now(), detail=str(exc))


def check_groq() -> ConnectionHealth:
    now = time.time()
    cached = _groq_health_cache["result"]

    if cached is not None and now < _groq_health_cache["expires_at"]:
        # Reuse the last real check's connected/detail verdict, but refresh
        # the timestamp — it's genuinely accurate to say "verified within
        # the last 30s", which is all this UI ever shows anyway.
        return ConnectionHealth(
            service="Groq",
            connected=cached.connected,
            last_checked=_now(),
            detail=cached.detail,
        )

    if not settings.GROQ_API_KEY:
        result = ConnectionHealth(
            service="Groq",
            connected=False,
            last_checked=_now(),
            detail="GROQ_API_KEY is not set",
        )
    else:
        try:
            from groq import Groq

            Groq(api_key=settings.GROQ_API_KEY).models.list()
            result = ConnectionHealth(service="Groq", connected=True, last_checked=_now())
        except Exception as exc:
            result = ConnectionHealth(service="Groq", connected=False, last_checked=_now(), detail=str(exc))

    _groq_health_cache["result"] = result
    _groq_health_cache["expires_at"] = now + _GROQ_HEALTH_TTL_SECONDS
    return result


def get_all_health() -> list[ConnectionHealth]:
    return [check_qdrant(), check_redis(), check_groq()]
