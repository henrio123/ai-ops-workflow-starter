"""Retrieval layer.

Component 3a provides the retrieval abstraction (the VectorStore protocol) and a
deterministic in-memory implementation for offline tests. The pgvector backend
is component 3b and will implement the same VectorStore protocol behind the same
contract. This package is import-safe: it pulls in no database client or vendor
SDK. The embedding provider comes from the LLM layer so retrieval stays
vendor-neutral.
"""

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
    "cosine_similarity",
]
