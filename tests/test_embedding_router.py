from src.agents.embedding_router import (
    EmbeddingRouter
)

# router = EmbeddingRouter()

# questions = [

#     "What is Machine Learning?",

#     "Summarize this document",

#     "How is Artificial Intelligence related to Security Analytics?",

#     "Compare machine learning and deep learning",

#     "Which section discusses neural networks?"
# ]

# for question in questions:

#     route = router.route(
#         question
#     )

#     print()

#     print(
#         f"Question: {question}"
#     )

#     print(
#         f"Route: {route}"
#     )


router = EmbeddingRouter()

scores = (
    router.route_with_bandit(
        "How is Artificial Intelligence related to Security Analytics?"
    )
)

print(scores)