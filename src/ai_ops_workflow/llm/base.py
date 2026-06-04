"""LLM provider and embedder interfaces (Phase 0 placeholder).

These small interfaces are the only LLM contract the core knows. Swapping
providers is a config or environment change, not a core code change.

Planned interfaces (illustrative, implemented in Phase 1):

    class LLMProvider(Protocol):
        def complete(self, prompt: str, *, system: str | None = None) -> str: ...
        def extract(self, prompt: str, schema: type[BaseModel]) -> BaseModel:
            # ask the model to fill `schema`, return a validated instance
            ...

    class Embedder(Protocol):
        def embed(self, texts: list[str]) -> list[list[float]]: ...

A provider may implement both, or an Embedder may be a separate adapter. The
core composes whichever it is given.

No logic in Phase 0.
"""
