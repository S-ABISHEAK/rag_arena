from src.graph.entity_extractor import (
    EntityExtractor
)

extractor = EntityExtractor()

result = extractor.extract(
    """
    Microsoft owns GitHub.

    GitHub hosts repositories.

    Developers contribute
    through pull requests.
    """
)

print(result)