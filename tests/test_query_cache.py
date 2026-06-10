from src.cache.query_cache import (
    QueryCache
)

cache = QueryCache()

cache.set(
    "What is AI?",
    {
        "answer":
        "Artificial Intelligence"
    }
)

result = cache.get(
    "What is AI?"
)

print()

print(result)