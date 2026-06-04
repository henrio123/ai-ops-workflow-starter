"""LLM and embedding provider interfaces (Phase 0 placeholder).

Two separate sibling protocols make up the LLM contract the core knows.
`LLMProvider` handles completion and extraction (the chat-style calls).
`EmbeddingProvider` handles embeddings for retrieval. They are deliberately
distinct: extraction and embeddings may use different providers, and retrieval
must not be coupled to whichever provider does extraction. The default planned
extraction provider for Phase 1 is Anthropic; the embedding provider is chosen
independently and is not assumed to be Anthropic. Swapping either is a config or
environment change, not a core code change.

Planned interfaces (illustrative, implemented in Phase 1):

    class LLMProvider(Protocol):
        def complete(self, prompt: str, *, system: str | None = None) -> str: ...
        def extract(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
            # ask the model to fill `schema`, return a validated instance
            ...

    class EmbeddingProvider(Protocol):
        def embed(self, texts: list[str]) -> list[list[float]]: ...

The two protocols are implemented by separate adapters (an extraction adapter
and an embedding adapter, which may be different vendors). The core composes
whichever pair it is given.

No logic in Phase 0.
"""
