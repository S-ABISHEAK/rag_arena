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