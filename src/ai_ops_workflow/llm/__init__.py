"""Provider-adapter LLM layer.

The core depends only on two separate sibling protocols in base.py, never on a
vendor SDK: `LLMProvider` for completion and extraction, and
`EmbeddingProvider` for embeddings used by retrieval. Keeping them distinct
means extraction and embeddings can use different providers, and retrieval is
not coupled to the chat/completion provider.

Only deterministic mock implementations are wired so far. Real extraction
adapters (Anthropic by default, plus OpenAI and local later) slot in behind the
same protocols. This package is import-safe: it pulls in no vendor library.
"""

from .base import (
    EmbeddingProvider,
    EmbeddingResult,
    ExtractionResult,
    LLMProvider,
    LLMResponse,
)
from .factory import get_embedding_provider, get_llm_provider
from .mock_provider import MockEmbeddingProvider, MockLLMProvider

__all__ = [
    "LLMProvider",
    "EmbeddingProvider",
    "LLMResponse",
    "ExtractionResult",
    "EmbeddingResult",
    "MockLLMProvider",
    "MockEmbeddingProvider",
    "get_llm_provider",
    "get_embedding_provider",
]
