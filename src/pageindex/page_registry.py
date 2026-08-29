import threading
from pathlib import Path
import json


class PageRegistry:

    # Class-level: see the identical note in DocumentRegistry — multiple
    # instances (resources.py's cached one, plus fresh ones each
    # PageIndexRAG/PageIndexBuilder constructs) share the same file and
    # must serialize through the same lock to avoid a lost-update race.
    _lock = threading.Lock()

    def __init__(
        self,
        registry_path: str = "data/pageindex/pages.json"
    ):

        self.registry_path = Path(
            registry_path
        )

        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.registry_path.exists():

            self._save([])

    def _load(self):

        with open(
            self.registry_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def _save(
        self,
        data
    ):

        with open(
            self.registry_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    def add_page(
        self,
        source: str,
        page_number: int,
        page_content: str,
        summary: str,
        chunk_ids: list[str]
    ):

        self.add_pages([
            {
                "source": source,
                "page_number": page_number,
                "page_content": page_content,
                "summary": summary,
                "chunk_ids": chunk_ids
            }
        ])

    def add_pages(
        self,
        pages: list[dict]
    ):
        """
        Append multiple pages in a single load/save round trip — used by
        PageIndexBuilder so indexing an N-page document does one file
        rewrite instead of N.
        """

        with self._lock:

            existing = self._load()

            existing.extend(pages)

            self._save(existing)

    def get_all_pages(self):

        return self._load()

    def get_page(
        self,
        source: str,
        page_number: int
    ):

        pages = self._load()

        for page in pages:

            if (
                page["source"] == source
                and
                page["page_number"] == page_number
            ):
                return page

        return None

    def clear(self):

        with self._lock:

            self._save([])
