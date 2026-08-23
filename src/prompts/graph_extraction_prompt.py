GRAPH_EXTRACTION_PROMPT = """
Extract entities and relationships.

Return ONLY valid JSON.

Format:

{{
  "entities": [
    "Entity1",
    "Entity2"
  ],
  "relationships": [
    {{
      "source": "Entity1",
      "relation": "relationship",
      "target": "Entity2"
    }}
  ]
}}

Text:

{text}
"""

GRAPH_EXTRACTION_BATCH_PROMPT = """
Extract entities and relationships from EACH of the following chunks.

Return ONLY a JSON array, one object per chunk, in the same order given,
with no other text:

[
  {{
    "index": <chunk index>,
    "entities": ["Entity1", "Entity2"],
    "relationships": [
      {{"source": "Entity1", "relation": "relationship", "target": "Entity2"}}
    ]
  }}
]

Chunks:

{chunks_block}
"""