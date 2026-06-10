from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from src.embeddings.embedder import (
    EmbeddingService
)

from src.agents.router_profiles import (
    RETRIEVER_PROFILES
)

from src.agents.contextual_bandit import (
    ContextualBandit
)


class EmbeddingRouter:

    def __init__(self):

        self.embedder = (
            EmbeddingService()
        )

        self.profile_embeddings = (
            self._build_profiles()
        )

        self.profile_embeddings = (
            self._build_profiles()
        )

        self.bandit = (
            ContextualBandit()
        )

    def _build_profiles(self):

        embeddings = {}

        for (
            retriever,
            description
        ) in RETRIEVER_PROFILES.items():

            embeddings[
                retriever
            ] = (
                self.embedder.embed_query(
                    description
                )
            )

        return embeddings

    def route(
        self,
        question: str
    ) -> str:

        query_embedding = (
            self.embedder.embed_query(
                question
            )
        )

        scores = {}

        for (
            retriever,
            embedding
        ) in self.profile_embeddings.items():

            similarity = (
                cosine_similarity(
                    np.array(
                        query_embedding
                    ).reshape(1, -1),
                    np.array(
                        embedding
                    ).reshape(1, -1)
                )[0][0]
            )

            scores[
                retriever
            ] = similarity

    def route_with_scores(
        self,
        question: str
    ):

        query_embedding = (
            self.embedder.embed_query(
                question
            )
        )

        scores = {}

        for (
            retriever,
            embedding
        ) in self.profile_embeddings.items():

            similarity = (
                cosine_similarity(
                    np.array(query_embedding).reshape(1, -1),
                    np.array(embedding).reshape(1, -1)
                )[0][0]
            )

            scores[retriever] = float(
                similarity
            )

        return dict(
            sorted(
                scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )

    def route_with_bandit(
        self,
        question: str
    ):    
        query_embedding = (
            self.embedder.embed_query(
                question
            )
        )

        scores = {}

        bandit_scores = (
            self.bandit
            .get_retriever_scores()
        )

        for (
            retriever,
            embedding
        ) in self.profile_embeddings.items():

            embedding_score = (
                cosine_similarity(
                    np.array(
                        query_embedding
                    ).reshape(1, -1),
                    np.array(
                        embedding
                    ).reshape(1, -1)
                )[0][0]
            )

            reward_score = (
                bandit_scores.get(
                    retriever,
                    0.5
                )
            )

            final_score = (
                0.8 * embedding_score
                +
                0.2 * reward_score
            )

            scores[
                retriever
            ] = {
                "embedding_score":
                float(
                    embedding_score
                ),

                "reward_score":
                float(
                    reward_score
                ),

                "final_score":
                float(
                    final_score
                )
            }

        return dict(
            sorted(
                scores.items(),
                key=lambda x:
                x[1]["final_score"],
                reverse=True
            )
        )