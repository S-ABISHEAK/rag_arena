PAGE_SELECTION_PROMPT = """
You are a retrieval system.

Question:
{question}

Available Pages:
{pages}

Rules:
- Return at most 3 page numbers.
- Return only page numbers.
- Do not explain.
- Use comma separated values.

Example:
1,4,7

Relevant Pages:
"""