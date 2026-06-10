class RewardFunction:

    @staticmethod
    def compute(
        latency: float
    ) -> float:

        return (
            1 /
            (1 + latency)
        )
    

    