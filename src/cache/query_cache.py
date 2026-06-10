import json
import hashlib

from src.cache.redis_client import (
    RedisClient
)


class QueryCache:

    def __init__(self):

        self.client = (
            RedisClient.get_client()
        )

    def _generate_key(
        self,
        query: str
    ) -> str:

        return hashlib.md5(
            query.encode()
        ).hexdigest()

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
                response
            )
        )