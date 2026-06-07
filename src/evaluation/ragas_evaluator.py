# from datasets import Dataset

# from ragas import evaluate

# from ragas.metrics import (
#     faithfulness,
#     answer_relevancy
# )


# class RagasEvaluator:

#     @staticmethod
import os
import logging
from datasets import Dataset
from ragas import evaluate

# Reverted back to the original import to bypass the Ragas type-checking bug
from ragas.metrics import faithfulness, answer_relevancy

from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from src.config.settings import settings

logger = logging.getLogger(__name__)


class RagasEvaluator:

    @staticmethod
    def evaluate_response(
        question: str,
        answer: str,
        context: list[str]
    ):

        # Build a small dataset for ragas (contexts is a list-of-strings per example)
        dataset = Dataset.from_dict(
            {
                "question": [question],
                "answer": [answer],
                "contexts": [context]
            }
        )

        try:
            # 1. Initialize the Groq LLM (Judge) using configured model
            groq_llm = ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model=settings.DEFAULT_LLM_MODEL,
                temperature=0.0,
                n=1
            )

            ragas_llm = LangchainLLMWrapper(groq_llm)

            # 2. Initialize HuggingFace Embeddings (used by some ragas metrics)
            hf_embeddings = HuggingFaceEmbeddings(
                model_name="BAAI/bge-small-en-v1.5"
            )
            ragas_embeddings = LangchainEmbeddingsWrapper(hf_embeddings)


            # --- THE GROQ FIX ---
            # Force the pre-instantiated answer_relevancy metric to only request 
            # 1 variant per API call, satisfying Groq's strict API limits.
            answer_relevancy.strictness = 1
            # 3. Run the evaluation per-metric so we can capture partial failures
            results = {}

            for metric in (faithfulness, answer_relevancy):
                metric_name = getattr(metric, "__name__", str(metric))

                try:
                    r = evaluate(
                        dataset=dataset,
                        metrics=[metric],
                        llm=ragas_llm,
                        embeddings=ragas_embeddings,
                    )

                    # r may be a dict-like containing the metric result
                    results[metric_name] = r

                except Exception as mexc:
                    logger.exception("Metric %s evaluation failed", metric_name)
                    # If Groq rejects an 'n' > 1 request, ragas may trigger
                    # a BadRequestError. As a pragmatic fallback, compute a
                    # simple embedding-based relevancy score so callers get
                    # a numeric result instead of NaN.
                    msg = str(mexc).lower()

                    if "number must be at most 1" in msg or "'n' : number must be at most 1" in msg:
                        try:
                            # Lazy import to avoid extra deps unless needed
                            from sentence_transformers import SentenceTransformer, util
                            import torch

                            embed_model_name = getattr(settings, 'EMBEDDING_MODEL', 'all-MiniLM-L6-v2')

                            # sentence-transformers model naming sometimes uses the short name
                            short_name = embed_model_name.split('/')[-1]

                            st_model = SentenceTransformer(short_name)

                            answer_emb = st_model.encode(answer, convert_to_tensor=True)

                            if context and len(context) > 0:
                                ctx_embs = [st_model.encode(c, convert_to_tensor=True) for c in context]
                                ctx_stack = torch.stack([e for e in ctx_embs])
                                ctx_mean = torch.mean(ctx_stack, dim=0)

                                sim = util.cos_sim(answer_emb, ctx_mean).item()

                                # Normalize similarity from [-1,1] to [0,1]
                                score = (sim + 1.0) / 2.0

                                results[metric_name] = {"fallback_answer_relevancy": round(score, 4)}
                            else:
                                results[metric_name] = {"fallback_answer_relevancy": None, "note": "no contexts"}

                        except Exception as fe:
                            logger.exception("Fallback relevancy computation failed")
                            results[metric_name] = {"error": str(mexc), "fallback_error": str(fe)}

                    else:
                        results[metric_name] = {"error": str(mexc)}

            return results

        except Exception as exc:
            # Log the full error and return a simple failure payload so callers
            # can inspect what went wrong without pytest failing hard.
            logger.exception("Ragas evaluation failed")

            return {
                "error": str(exc),
                "faithfulness": None,
                "answer_relevancy": None
            }
            