from src.api.schemas import RagasScore


def _extract_score(metric_name: str, raw_result) -> tuple[float | None, bool]:
    """Best-effort extraction of a numeric score from whatever shape
    RagasEvaluator.evaluate_response() produced for one metric.

    Returns (score, approximate). Returns (None, False) if nothing usable
    could be extracted — callers must surface that as missing data, never
    invent a number.
    """

    if isinstance(raw_result, dict):
        if "fallback_answer_relevancy" in raw_result:
            return raw_result["fallback_answer_relevancy"], True
        if "error" in raw_result:
            return None, False
        for key, value in raw_result.items():
            if isinstance(value, (int, float)):
                return float(value), False
        return None, False

    try:
        return float(raw_result[metric_name]), False
    except Exception:
        pass

    try:
        df = raw_result.to_pandas()
        return float(df[metric_name].mean()), False
    except Exception:
        pass

    return None, False


def normalize_ragas_result(raw: dict) -> RagasScore:
    if "error" in raw and "faithfulness" in raw and raw.get("faithfulness") is None:
        # Top-level failure path from RagasEvaluator's outer except block.
        return RagasScore(error=raw["error"])

    faithfulness = None
    answer_relevancy = None
    approximate = False
    error = None

    for metric_name, metric_result in raw.items():
        lowered = metric_name.lower()

        if isinstance(metric_result, dict) and "error" in metric_result and "fallback_answer_relevancy" not in metric_result:
            error = metric_result["error"]
            continue

        score, is_approx = _extract_score(metric_name, metric_result)
        approximate = approximate or is_approx

        if "faith" in lowered:
            faithfulness = score
        elif "relev" in lowered:
            answer_relevancy = score

    return RagasScore(
        faithfulness=faithfulness,
        answer_relevancy=answer_relevancy,
        approximate=approximate or None,
        error=error,
    )
