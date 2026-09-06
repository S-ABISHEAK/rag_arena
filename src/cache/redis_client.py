import redis

from src.config.settings import settings


class RedisClient:

    _client = None

    @classmethod
    def get_client(cls):

        if cls._client is None:

            # Was hardcoded to "localhost" — worked only because local dev
            # runs Redis on the same host. Any real deployment (Docker
            # network, managed Redis, separate host) needs this configurable,
            # same as QdrantStore already is.
            cls._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )

        return cls._client