from langchain_core.documents import Document


def format_sources(
    documents: list[Document]
) -> list[dict]:

    formatted = []

    for doc in documents:

        formatted.append(
            {
                "source": doc.metadata.get(
                    "source"
                ),
                "page": doc.metadata.get(
                    "page"
                ),
                "chunk_id": doc.metadata.get(
                    "chunk_id"
                )
            }
        )

    return formatted