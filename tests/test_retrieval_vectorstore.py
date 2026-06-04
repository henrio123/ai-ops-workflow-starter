"""Tests for the retrieval abstraction and in-memory vector store (3a).

All deterministic and offline: no network, no database, no LLM, no spend.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_ops_workflow.core.models import RetrievedSnippet
from ai_ops_workflow.llm.base import EmbeddingResult
from ai_ops_workflow.llm.mock_provider import MockEmbeddingProvider
from ai_ops_workflow.retrieval import (
    InMemoryVectorStore,
    SnippetToIndex,
    VectorSearchQuery,
    VectorStore,
    cosine_similarity,
)


class FixedEmbeddingProvider:
    """Test-only provider mapping known texts to fixed vectors (no service)."""

    def __init__(self, mapping: dict[str, list[float]], dimensions: int = 2) -> None:
        self._mapping = mapping
        self._dimensions = dimensions

    @property
    def dimension(self) -> int:
        return self._dimensions

    def embed(self, texts: list[str]) -> EmbeddingResult:
        vectors = [list(self._mapping[text]) for text in texts]
        return EmbeddingResult(
            embeddings=vectors, model="fixed", provider="test"
        )


class WrongCountProvider:
    """Test-only provider returning the wrong number of vectors."""

    @property
    def dimension(self) -> int:
        return 8

    def embed(self, texts: list[str]) -> EmbeddingResult:
        return EmbeddingResult(
            embeddings=[[0.0] * 8], model="bad-count", provider="test"
        )


class WrongDimProvider:
    """Test-only provider returning vectors of the wrong length."""

    @property
    def dimension(self) -> int:
        return 8

    def embed(self, texts: list[str]) -> EmbeddingResult:
        return EmbeddingResult(
            embeddings=[[0.0, 0.0, 0.0] for _ in texts],
            model="bad-dim",
            provider="test",
        )


def test_snippet_to_index_validates():
    snippet = SnippetToIndex(source_id="RULE-01", text="rule text")
    assert snippet.source_id == "RULE-01"
    assert snippet.metadata == {}


def test_snippet_to_index_rejects_empty_fields():
    with pytest.raises(ValidationError):
        SnippetToIndex(source_id="", text="text")
    with pytest.raises(ValidationError):
        SnippetToIndex(source_id="RULE-01", text="   ")


def test_vector_search_query_validates():
    query = VectorSearchQuery(text="find this")
    assert query.top_k == 4


def test_vector_search_query_rejects_blank_text_and_bad_top_k():
    with pytest.raises(ValidationError):
        VectorSearchQuery(text="   ")
    with pytest.raises(ValidationError):
        VectorSearchQuery(text="ok", top_k=0)


def test_cosine_similarity_identical_vectors():
    assert cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_similarity_zero_vector():
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


def test_cosine_similarity_mismatched_lengths_raises():
    with pytest.raises(ValueError):
        cosine_similarity([1.0, 2.0], [1.0])


def test_cosine_similarity_empty_vector_raises():
    with pytest.raises(ValueError):
        cosine_similarity([], [])


def test_upsert_rejects_empty_list():
    store = InMemoryVectorStore(MockEmbeddingProvider())
    with pytest.raises(ValueError):
        store.upsert_snippets([])


def test_upsert_stores_and_returns_count():
    store = InMemoryVectorStore(MockEmbeddingProvider())
    count = store.upsert_snippets(
        [
            SnippetToIndex(source_id="A-1", text="alpha"),
            SnippetToIndex(source_id="B-2", text="beta"),
        ]
    )
    assert count == 2
    assert store.count() == 2


def test_upsert_replaces_by_source_id():
    store = InMemoryVectorStore(MockEmbeddingProvider())
    store.upsert_snippets([SnippetToIndex(source_id="A-1", text="alpha")])
    store.upsert_snippets(
        [SnippetToIndex(source_id="A-1", text="alpha v2", metadata={"v": "2"})]
    )
    assert store.count() == 1
    results = store.search(VectorSearchQuery(text="alpha v2", top_k=5))
    assert len(results) == 1
    assert results[0].text == "alpha v2"
    assert results[0].metadata == {"v": "2"}


def test_upsert_rejects_embedding_count_mismatch():
    store = InMemoryVectorStore(WrongCountProvider())
    with pytest.raises(ValueError):
        store.upsert_snippets(
            [
                SnippetToIndex(source_id="A-1", text="alpha"),
                SnippetToIndex(source_id="B-2", text="beta"),
            ]
        )


def test_upsert_rejects_vector_dimension_mismatch():
    store = InMemoryVectorStore(WrongDimProvider())
    with pytest.raises(ValueError):
        store.upsert_snippets([SnippetToIndex(source_id="A-1", text="alpha")])


def test_search_returns_empty_when_store_empty():
    store = InMemoryVectorStore(MockEmbeddingProvider())
    assert store.search(VectorSearchQuery(text="anything")) == []


def test_search_ranks_by_descending_score():
    mapping = {
        "query": [1.0, 0.0],
        "identical": [1.0, 0.0],
        "diagonal": [1.0, 1.0],
        "orthogonal": [0.0, 1.0],
    }
    store = InMemoryVectorStore(FixedEmbeddingProvider(mapping))
    store.upsert_snippets(
        [
            SnippetToIndex(source_id="ORTH", text="orthogonal"),
            SnippetToIndex(source_id="DIAG", text="diagonal"),
            SnippetToIndex(source_id="IDENT", text="identical"),
        ]
    )
    results = store.search(VectorSearchQuery(text="query", top_k=3))
    assert [r.source_id for r in results] == ["IDENT", "DIAG", "ORTH"]
    assert results[0].score == pytest.approx(1.0)
    assert results[-1].score == pytest.approx(0.0)
    for r in results:
        assert isinstance(r, RetrievedSnippet)
        assert 0.0 <= r.score <= 1.0


def test_search_respects_top_k():
    mapping = {
        "query": [1.0, 0.0],
        "a": [1.0, 0.0],
        "b": [1.0, 1.0],
        "c": [0.0, 1.0],
    }
    store = InMemoryVectorStore(FixedEmbeddingProvider(mapping))
    store.upsert_snippets(
        [
            SnippetToIndex(source_id="A", text="a"),
            SnippetToIndex(source_id="B", text="b"),
            SnippetToIndex(source_id="C", text="c"),
        ]
    )
    results = store.search(VectorSearchQuery(text="query", top_k=2))
    assert len(results) == 2


def test_search_tie_break_by_source_id_ascending():
    mapping = {"query": [1.0, 0.0], "same": [1.0, 0.0]}
    store = InMemoryVectorStore(FixedEmbeddingProvider(mapping))
    store.upsert_snippets(
        [
            SnippetToIndex(source_id="Z-9", text="same"),
            SnippetToIndex(source_id="A-1", text="same"),
        ]
    )
    first = store.search(VectorSearchQuery(text="query", top_k=2))
    second = store.search(VectorSearchQuery(text="query", top_k=2))
    assert [r.source_id for r in first] == ["A-1", "Z-9"]
    assert [r.source_id for r in first] == [r.source_id for r in second]


def test_search_query_dimension_mismatch_raises():
    store = InMemoryVectorStore(MockEmbeddingProvider(dimensions=8))
    store.upsert_snippets([SnippetToIndex(source_id="A-1", text="alpha")])
    # Swap in a provider whose query vector length differs from its dimension.
    store._embedding_provider = WrongDimProvider()
    with pytest.raises(ValueError):
        store.search(VectorSearchQuery(text="alpha"))


def test_in_memory_store_satisfies_protocol():
    assert isinstance(InMemoryVectorStore(MockEmbeddingProvider()), VectorStore)


def test_retrieval_package_has_no_forbidden_domain_terms():
    repo_root = Path(__file__).resolve().parents[1]
    retrieval_dir = repo_root / "src" / "ai_ops_workflow" / "retrieval"
    forbidden = ("quarry", "aggregate", "gravel", "tonnes", "kruusakarjaar")
    py_files = list(retrieval_dir.glob("*.py"))
    assert py_files, "expected retrieval python files to scan"
    for path in py_files:
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden:
            assert term not in text, f"forbidden term '{term}' found in {path}"
