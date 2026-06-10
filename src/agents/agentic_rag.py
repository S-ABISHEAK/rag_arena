from src.agents.router import (
    Router
)

from src.retrieval.traditional_rag import (
    TraditionalRAG
)

from src.retrieval.hybrid_rag import (
    HybridRAG
)

from src.retrieval.pageindex_rag import (
    PageIndexRAG
)

from src.retrieval.graph_rag import (
    GraphRAG
)

from src.cache.query_cache import (
    QueryCache
)


class AgenticRAG:

    def __init__(self):

        self.router = (
            Router()
        )

        self.traditional_rag = (
            TraditionalRAG()
        )

        self.hybrid_rag = (
            HybridRAG()
        )

        self.pageindex_rag = (
            PageIndexRAG()
        )

        self.graph_rag = (
            GraphRAG()
        )

        self.cache = (
            QueryCache()
        )

    def query(
        self,
        question: str
    ):

        cached_response = (
            self.cache.get(
                question
            )
        )

        if cached_response:

            cached_response[
                "cache_hit"
            ] = True

            return cached_response

        route = (
            self.router.route(
                question
            )
        )

        if route == "GRAPH":

            response = (
                self.graph_rag.query(
                    question
                )
            )

        elif route == "PAGEINDEX":

            response = (
                self.pageindex_rag.query(
                    question
                )
            )

        elif route == "HYBRID":

            response = (
                self.hybrid_rag.query(
                    question
                )
            )

        else:

            response = (
                self.traditional_rag.query(
                    question
                )
            )

        response[
            "selected_strategy"
        ] = route

        response[
            "cache_hit"
        ] = False

        self.cache.set(
            query=question,
            response=response
        )

        return response