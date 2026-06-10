from src.agents.contextual_bandit import (
    ContextualBandit
)

bandit = ContextualBandit()

print()

print(
    bandit.get_retriever_scores()
)