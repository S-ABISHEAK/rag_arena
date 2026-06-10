from src.agents.reward_tracker import (
    RewardTracker
)


class ContextualBandit:

    def __init__(self):

        self.tracker = (
            RewardTracker()
        )

    def average_reward(
        self,
        retriever: str
    ) -> float:

        history = (
            self.tracker
            .get_retriever_history(
                retriever
            )
        )

        if len(history) < 5:
            return 0.65

        rewards = [
            item["reward"]
            for item in history
        ]

        return (
            sum(rewards)
            / len(rewards)
        )

    def get_retriever_scores(
        self
    ):

        retrievers = [

            "TRADITIONAL",

            "HYBRID",

            "PAGEINDEX",

            "GRAPH"

        ]

        return {
            retriever:
            self.average_reward(
                retriever
            )
            for retriever
            in retrievers
        }