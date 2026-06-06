import time


class Metrics:

    @staticmethod
    def measure_latency(
        start_time: float,
        end_time: float
    ) -> float:

        return round(
            end_time - start_time,
            4
        )