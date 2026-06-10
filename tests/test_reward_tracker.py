from src.agents.reward_tracker import (
    RewardTracker
)

from src.agents.reward_function import (
    RewardFunction
)

tracker = RewardTracker()

tracker.record_result(
    question="What is AI?",
    retriever="TRADITIONAL",
    latency=1.2,
    reward=0.8
)

print()

print(
    tracker.load_history()
)


print(
    RewardFunction.compute(
        0.5
    )
)

print(
    RewardFunction.compute(
        2.0
    )
)