"""Retrieval layer.

Component 3a provides the retrieval abstraction (the VectorStore protocol) and a
deterministic in-memory implementation for offline tests. Component 3b adds
PgVectorStore, a real pgvector-backed implementation behind the same protocol.
The pgvector backend takes an injected connection and never opens one itself, so
importing this package stays import-safe: it pulls in no database client or
vendor SDK at load time. The embedding provider comes from the LLM layer so
retrieval stays vendor-neutral.
"""

from .pgvector_store import PgVectorStore
from .vectorstore import (
    InMemoryVectorStore,
    SnippetToIndex,
    VectorSearchQuery,
    VectorStore,
    cosine_similarity,
)

__all__ = [
    "SnippetToIndex",
    "VectorSearchQuery",
    "VectorStore",
    "InMemoryVectorStore",
    "PgVectorStore",
    "cosine_similarity",
]
