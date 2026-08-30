"""
Compatibility shim for an upstream ragas 0.4.3 bug: ragas/llms/base.py
unconditionally imports `langchain_community.chat_models.vertexai.ChatVertexAI`
at module load time, but that submodule was removed from current
langchain_community releases (Vertex AI chat support moved to the separate
`langchain-google-vertexai` package). Without this shim, `import ragas`
fails outright with `ModuleNotFoundError`.

This project only ever evaluates through Groq (see RagasEvaluator below),
never Vertex AI, so a real implementation isn't needed — this stub exists
purely to satisfy ragas's import so the rest of the library (which we do
use) can load. If it's ever actually instantiated, it raises clearly rather
than pretending to work.

Downgrading langchain_community to a version that still has this module is
not a safe alternative: it would force langchain-core<1.0.0, which cascades
into downgrading langchain-groq/langchain-huggingface/langchain-qdrant —
i.e. breaking the parts of this project that currently work, to fix the one
that doesn't.

Must be imported before `ragas` anywhere in this codebase — see the import
at the top of ragas_evaluator.py.
"""

import sys
import types


def _install_vertexai_chat_models_stub() -> None:
    module_name = "langchain_community.chat_models.vertexai"

    if module_name in sys.modules:
        return

    try:
        __import__(module_name)
        return  # a real implementation exists in this environment — no-op
    except ModuleNotFoundError:
        pass

    stub = types.ModuleType(module_name)

    class ChatVertexAI:  # pragma: no cover - never meant to be instantiated
        def __init__(self, *args, **kwargs):
            raise RuntimeError(
                "ChatVertexAI is a compatibility stub (see "
                "src/evaluation/_ragas_compat.py) satisfying a ragas import "
                "— this project only supports Groq, not Vertex AI."
            )

    stub.ChatVertexAI = ChatVertexAI
    sys.modules[module_name] = stub

    import langchain_community.chat_models as chat_models_pkg
    chat_models_pkg.vertexai = stub


_install_vertexai_chat_models_stub()
