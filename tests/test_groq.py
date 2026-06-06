from src.llm.groq_client import GroqLLM


llm = GroqLLM()

response = llm.invoke(
    "What is Retrieval Augmented Generation?"
)

print(response)