import hashlib
import json
from pathlib import Path
from typing import Any


class ContentCache:
    """
    Persists LLM outputs keyed by a hash of their input text, so re-indexing
    identical content (a re-uploaded PDF, a duplicated page) never re-calls
    the LLM for something it already has an answer for.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}

        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self._data, file)

    @staticmethod
    def key_for(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> Any | None:
        return self._data.get(self.key_for(text))

    def set(self, text: str, value: Any) -> None:
        self._data[self.key_for(text)] = value
        self._save()
