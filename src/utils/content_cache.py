import hashlib
import json
import threading
from pathlib import Path
from typing import Any

# Keyed by resolved path, not a single shared lock, so caches at different
# paths (page summaries vs entity extractions) don't serialize against each
# other — but any two ContentCache instances pointing at the *same* file
# (however they were constructed) always share the same lock.
_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _lock_for(path: Path) -> threading.Lock:
    key = str(path.resolve())
    if key not in _locks:
        with _locks_guard:
            if key not in _locks:
                _locks[key] = threading.Lock()
    return _locks[key]


class ContentCache:
    """
    Persists LLM outputs keyed by a hash of their input text, so re-indexing
    identical content (a re-uploaded PDF, a duplicated page) never re-calls
    the LLM for something it already has an answer for.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file_lock = _lock_for(self.path)
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
        with self._file_lock:
            # Re-read the latest on-disk state before merging: another
            # ContentCache instance on the same path may have written
            # since this one's _data was loaded, and this must not
            # silently discard those entries.
            on_disk = self._load()
            on_disk[self.key_for(text)] = value
            self._data = on_disk
            self._save()
