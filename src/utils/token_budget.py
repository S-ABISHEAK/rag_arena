# Groq's free/on-demand tier caps this project at 8,000 tokens/minute and
# 200,000 tokens/day (see settings.py) — far tighter than the model's own
# 131k context window. The context window is not the real constraint here;
# the per-minute/per-day budget is. These helpers keep every prompt this
# project builds (retrieved context, page-summary/entity-extraction
# batches) within a sane token budget so a single oversized page or a
# generous TOP_K doesn't consume the whole minute's allowance in one call.
#
# There's no local tokenizer for every model this project might point at
# (Groq's various hosted models), so token counts here are a deliberately
# conservative estimate — roughly 4 characters per token for English text,
# a widely-used approximation (see e.g. OpenAI's own rule of thumb). It
# only needs to be "safe enough to truncate before a real limit is hit",
# not exact.

CHARS_PER_TOKEN_ESTIMATE = 4


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN_ESTIMATE)


def truncate_to_token_budget(text: str, max_tokens: int) -> str:
    max_chars = max_tokens * CHARS_PER_TOKEN_ESTIMATE

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n[...truncated to fit the token budget...]"
