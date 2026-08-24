PAGE_SELECTION_PROMPT = """
You are a retrieval system.

Question:
{question}

Available Pages:
{pages}

Rules:
- Each page is labeled with a unique Page ID — always answer with Page IDs,
  never with the document's own page number, since multiple documents can
  share the same page number.
- Return at most 3 Page IDs.
- Return only Page IDs.
- Do not explain.
- Use comma separated values.

Example:
1,4,7

Relevant Page IDs:
"""