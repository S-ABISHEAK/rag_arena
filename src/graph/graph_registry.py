from pathlib import Path
import pickle


class GraphRegistry:

    def __init__(
        self,
        graph_path: str = "data/graph/graph.pkl"
    ):

        self.graph_path = Path(
            graph_path
        )

        self.graph_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def save_graph(
        self,
        graph
    ):

        with open(
            self.graph_path,
            "wb"
        ) as file:

            pickle.dump(
                graph,
                file
            )

    def load_graph(
        self
    ):

        if not self.graph_path.exists():

            return None

        with open(
            self.graph_path,
            "rb"
        ) as file:

            return pickle.load(
                file
            )

    def exists(
        self
    ) -> bool:

        return (
            self.graph_path.exists()
        )

    def clear(
        self
    ):

        if self.graph_path.exists():

            self.graph_path.unlink()