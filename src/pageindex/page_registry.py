from pathlib import Path
import json


class PageRegistry:

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

        pages = self._load()

        pages.append(
            {
                "source": source,
                "page_number": page_number,
                "page_content": page_content,
                "summary": summary,
                "chunk_ids": chunk_ids
            }
        )

        self._save(pages)

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

        self._save([])