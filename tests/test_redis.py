from src.cache.redis_client import (
    RedisClient
)

client = (
    RedisClient.get_client()
)

client.set(
    "test",
    "hello"
)

print(
    client.get(
        "test"
    )
)