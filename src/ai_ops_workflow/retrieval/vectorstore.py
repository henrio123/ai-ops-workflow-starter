"""Retrieval abstraction and in-memory vector store (Phase 1 component 3a).

Defines a backend-agnostic retrieval contract (the VectorStore protocol) plus a
deterministic in-memory implementation for offline tests. The pgvector backend
(component 3b) will implement the same VectorStore protocol; this module imports
no database client or vendor SDK and makes no network call. Cosine similarity is
pure-Python using the standard library only.
"""

from __future__ import annotations

import math
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, Field, field_validator

from ..core.models import RetrievedSnippet
from ..llm.base import EmbeddingProvider


class SnippetToIndex(BaseModel):
    """A snippet supplied for indexing, before it is embedded and stored."""

    source_id: str = Field(description="Citation key identifying the snippet source.")
    text: str = Field(description="The snippet text to embed and index.")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional free-form snippet metadata."
    )

    @field_validator("source_id", "text")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value


class VectorSearchQuery(BaseModel):
    """A retrieval query: free text plus how many results to return."""

    text: str = Field(description="The query text to embed and search with.")
    top_k: int = Field(default=4, description="Maximum number of results to return.")

    @field_validator("text")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value

    @field_validator("top_k")
    @classmethod
    def _top_k_positive(cls, value: int) -> int:
        if value < 1:
            raise ValueError("top_k must be at least 1")
        return value


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity of two equal-length, non-empty vectors, clamped to 0..1.

    Raises ValueError if the lengths differ or either vector is empty. Returns
    0.0 if either vector has zero norm. The result is clamped to [0.0, 1.0] so
    tiny floating-point drift does not push a retrieval score out of range.
    """

    if len(a) != len(b):
        raise ValueError("vectors must have the same length")
    if not a or not b:
        raise ValueError("vectors must be non-empty")

    dot = math.fsum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(math.fsum(x * x for x in a))
    norm_b = math.sqrt(math.fsum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    score = dot / (norm_a * norm_b)
    return max(0.0, min(1.0, score))


def _validate_vector_dimension(vector: list[float], expected: int) -> None:
    """Raise ValueError if `vector` does not have the expected length."""

    if len(vector) != expected:
        raise ValueError(
            f"expected vector of dimension {expected}, got {len(vector)}"
        )


@runtime_checkable
class VectorStore(Protocol):
    """Backend-agnostic retrieval contract. No vendor type appears here."""

    def upsert_snippets(self, snippets: list[SnippetToIndex]) -> int:
        """Embed and store snippets, replacing any with the same source_id."""
        ...

    def search(self, query: VectorSearchQuery) -> list[RetrievedSnippet]:
        """Return the top-k stored snippets most similar to the query text."""
        ...

    def count(self) -> int:
        """Return the number of unique stored snippets."""
        ...


class InMemoryVectorStore:
    """Deterministic in-memory VectorStore for offline tests.

    Holds each snippet and its embedding keyed by source_id, so upsert replaces
    by source_id. No database, no network, no domain logic.
    """

    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self._embedding_provider = embedding_provider
        self._records: dict[str, tuple[SnippetToIndex, list[float]]] = {}

    def upsert_snippets(self, snippets: list[SnippetToIndex]) -> int:
        if not snippets:
            raise ValueError("snippets must be a non-empty list")

        embeddings = self._embedding_provider.embed(
            [snippet.text for snippet in snippets]
        ).embeddings
        if len(embeddings) != len(snippets):
            raise ValueError(
                f"embedding count {len(embeddings)} does not match "
                f"snippet count {len(snippets)}"
            )

        expected = self._embedding_provider.dimension
        for vector in embeddings:
            _validate_vector_dimension(vector, expected)

        for snippet, vector in zip(snippets, embeddings):
            self._records[snippet.source_id] = (snippet, vector)
        return len(snippets)

    def search(self, query: VectorSearchQuery) -> list[RetrievedSnippet]:
        if not self._records:
            return []

        query_vector = self._embedding_provider.embed([query.text]).embeddings[0]
        _validate_vector_dimension(query_vector, self._embedding_provider.dimension)

        results: list[RetrievedSnippet] = []
        for snippet, vector in self._records.values():
            score = cosine_similarity(query_vector, vector)
            results.append(
                RetrievedSnippet(
                    source_id=snippet.source_id,
                    text=snippet.text,
                    score=score,
                    metadata=snippet.metadata,
                )
            )

        results.sort(key=lambda snippet: (-snippet.score, snippet.source_id))
        return results[: query.top_k]

    def count(self) -> int:
        return len(self._records)
