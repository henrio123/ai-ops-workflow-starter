"""Provider factory (Phase 1 component 2).

Resolves which provider adapter to use by name, so the core never names a
vendor. Only the deterministic mock providers are wired so far; importing this
module requires no vendor library and makes no network call. Real adapters
(for example Anthropic) are added later behind the same protocols.
"""

from __future__ import annotations

from .base import EmbeddingProvider, LLMProvider
from .mock_provider import MockEmbeddingProvider, MockLLMProvider


def get_llm_provider(name: str = "mock") -> LLMProvider:
    """Return an LLMProvider by name. Only "mock" is wired so far."""

    if name == "mock":
        return MockLLMProvider()
    raise ValueError(f"Unsupported LLM provider: {name}")


def get_embedding_provider(name: str = "mock") -> EmbeddingProvider:
    """Return an EmbeddingProvider by name. Only "mock" is wired so far."""

    if name == "mock":
        return MockEmbeddingProvider()
    raise ValueError(f"Unsupported embedding provider: {name}")
