"""Provider-adapter LLM layer.

The core depends only on two separate sibling protocols in base.py, never on a
vendor SDK: `LLMProvider` for completion and extraction, and
`EmbeddingProvider` for embeddings used by retrieval. Keeping them distinct
means extraction and embeddings can use different providers, and retrieval is
not coupled to the chat/completion provider.

Extraction implementations (Anthropic by default for Phase 1, plus mock, with
OpenAI and local planned later) can be swapped via config or environment without
changing any core node. The embedding provider is chosen independently and is
not assumed to be Anthropic.

Phase 0: placeholder modules only.
"""
