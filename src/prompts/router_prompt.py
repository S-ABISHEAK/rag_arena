ROUTER_PROMPT = """
Choose the best retrieval strategy.

Options:

TRADITIONAL
HYBRID
PAGEINDEX
GRAPH

Rules:

- GRAPH:
  entity relationships
  ownership
  connections
  dependencies

- PAGEINDEX:
  document structure
  sections
  pages
  summaries

- HYBRID:
  keyword + semantic search

- TRADITIONAL:
  general factual retrieval

Question:

{question}

Return ONLY one option.
"""