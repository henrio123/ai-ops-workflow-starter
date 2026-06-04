"""Mock provider adapter (Phase 0 placeholder).

A deterministic, offline implementation of the LLMProvider (and EmbeddingProvider)
interface for tests and local runs. Part of the design from the start, not an
afterthought: it lets the graph, retrieval, and audit be exercised without
network calls or spend. Returns canned, schema-valid fields and stable fake
embeddings so tests are reproducible.

Planned shape (Phase 1):

    class MockProvider:
        def complete(self, prompt, *, system=None) -> str: ...
        def extract(self, prompt, schema) -> BaseModel: ...   # canned valid data
        def embed(self, texts) -> list[list[float]]: ...      # deterministic

No logic in Phase 0.
"""
