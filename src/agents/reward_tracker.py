import threading
import json

from datetime import datetime, timezone
from pathlib import Path


class RewardTracker:

    # Class-level: see the identical note in DocumentRegistry.
    _lock = threading.Lock()

    def __init__(
        self,
        file_path: str = (
            "data/router/rewards.json"
        )
    ):

        self.file_path = Path(
            file_path
        )

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.file_path.exists():

            self.save_history([])

    def load_history(
        self
    ) -> list:

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    def save_history(
        self,
        history: list
    ):

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4
            )

    def record_result(
        self,
        question: str,
        retriever: str,
        latency: float,
        reward: float
    ):

        with self._lock:

            history = (
                self.load_history()
            )

            history.append(
                {
                    "question": question,
                    "retriever": retriever,
                    "latency": latency,
                    "reward": reward,
                    # Real wall-clock time of the recorded query — lets the
                    # UI show genuine recency/trend metrics instead of
                    # relying on array order as a proxy for time.
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            )

            self.save_history(
                history
            )

    def get_retriever_history(
        self,
        retriever: str
    ):

        history = (
            self.load_history()
        )

        return [
            record
            for record in history
            if record["retriever"]
            == retriever
        ]