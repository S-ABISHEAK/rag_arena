import json
import hashlib

from src.cache.redis_client import (
    RedisClient
)

from src.config.session import get_session_id


class QueryCache:

    def __init__(self):

        self.client = (
            RedisClient.get_client()
        )

    def _generate_key(
        self,
        query: str
    ) -> str:

        # Namespaced by session: two sessions have different indexed
        # documents, so even an identical question text must never return
        # one session's cached answer to another — that would leak content
        # and could hand back an answer about a document the asker never
        # uploaded.
        digest = hashlib.md5(
            query.encode()
        ).hexdigest()

        return f"{get_session_id()}:{digest}"

    def get(
        self,
        query: str
    ):

        key = self._generate_key(
            query
        )

        cached_response = (
            self.client.get(
                key
            )
        )

        if cached_response:

            return json.loads(
                cached_response
            )

        return None

    def set(
        self,
        query: str,
        response: dict,
        ttl: int = 3600
    ):

        key = self._generate_key(
            query
        )

        self.client.setex(
            key,
            ttl,
            json.dumps(
            response,
            default=str
        )
        )