"""Tests for the pgvector backend (component 3b) using a fake connection.

All deterministic and offline: no real database, no network, no LLM, no spend.
A FakeConnection/FakeCursor record the SQL and parameters the store emits and
return preset rows, so we assert on SQL shape and row mapping without Postgres.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from ai_ops_workflow.core.models import RetrievedSnippet
from ai_ops_workflow.llm.base import EmbeddingResult
from ai_ops_workflow.llm.mock_provider import MockEmbeddingProvider
from ai_ops_workflow.retrieval import (
    PgVectorStore,
    SnippetToIndex,
    VectorSearchQuery,
    VectorStore,
)
from ai_ops_workflow.retrieval.pgvector_store import _vector_to_pgvector


class FakeCursor:
    """Records every (sql, params) executed and returns preset rows."""

    def __init__(self, calls: list[tuple[str, Any]], rows: list[tuple]) -> None:
        self._calls = calls
        self._rows = rows

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *exc: object) -> bool:
        return False

    def execute(self, sql: str, params: object = None) -> None:
        self._calls.append((sql, params))

    def fetchall(self) -> list[tuple]:
        return list(self._rows)

    def fetchone(self) -> tuple | None:
        return self._rows[0] if self._rows else None


class FakeConnection:
    """Hands out cursors that share one recording list; records commit() calls."""

    def __init__(self, rows: list[tuple] | None = None) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.commits = 0
        self._rows = rows or []

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.calls, self._rows)

    def commit(self) -> None:
        self.commits += 1


class SmallCountProvider:
    """Returns the wrong number of vectors (one) regardless of input count."""

    @property
    def dimension(self) -> int:
        return 8

    def embed(self, texts: list[str]) -> EmbeddingResult:
        return EmbeddingResult(
            embeddings=[[0.0] * 8], model="bad-count", provider="test"
        )


class SmallDimProvider:
    """Returns vectors of the wrong length (three) for an 8-dim provider."""

    @property
    def dimension(self) -> int:
        return 8

    def embed(self, texts: list[str]) -> EmbeddingResult:
        return EmbeddingResult(
            embeddings=[[0.0, 0.0, 0.0] for _ in texts],
            model="bad-dim",
            provider="test",
        )


def test_rejects_unsafe_table_names():
    provider = MockEmbeddingProvider(dimensions=8)
    for bad in ("bad-name", "1table", "table;drop", ""):
        with pytest.raises(ValueError):
            PgVectorStore(FakeConnection(), provider, table_name=bad)


def test_accepts_safe_table_name():
    store = PgVectorStore(
        FakeConnection(), MockEmbeddingProvider(dimensions=8),
        table_name="policy_snippets",
    )
    assert store.table_name == "policy_snippets"


def test_ensure_schema_emits_ddl_and_commits():
    conn = FakeConnection()
    store = PgVectorStore(conn, MockEmbeddingProvider(dimensions=8))
    store.ensure_schema()

    sql_text = " ".join(sql for sql, _ in conn.calls)
    assert "CREATE EXTENSION IF NOT EXISTS vector" in sql_text
    assert "CREATE TABLE IF NOT EXISTS" in sql_text
    assert "VECTOR(8)" in sql_text
    assert conn.commits == 1


def test_upsert_rejects_empty_list():
    store = PgVectorStore(FakeConnection(), MockEmbeddingProvider(dimensions=8))
    with pytest.raises(ValueError):
        store.upsert_snippets([])


def test_upsert_emits_conflict_sql_per_snippet_and_commits():
    conn = FakeConnection()
    store = PgVectorStore(conn, MockEmbeddingProvider(dimensions=8))
    count = store.upsert_snippets(
        [
            SnippetToIndex(source_id="A-1", text="alpha"),
            SnippetToIndex(source_id="B-2", text="beta"),
        ]
    )
    assert count == 2

    inserts = [(sql, params) for sql, params in conn.calls if "INSERT INTO" in sql]
    assert len(inserts) == 2
    for sql, params in inserts:
        assert "ON CONFLICT" in sql
        assert "%s::vector" in sql
        assert len(params) == 4
    assert conn.commits == 1


def test_upsert_rejects_embedding_count_mismatch():
    store = PgVectorStore(FakeConnection(), SmallCountProvider())
    with pytest.raises(ValueError):
        store.upsert_snippets(
            [
                SnippetToIndex(source_id="A-1", text="alpha"),
                SnippetToIndex(source_id="B-2", text="beta"),
            ]
        )


def test_upsert_rejects_vector_dimension_mismatch():
    store = PgVectorStore(FakeConnection(), SmallDimProvider())
    with pytest.raises(ValueError):
        store.upsert_snippets([SnippetToIndex(source_id="A-1", text="alpha")])


def test_search_emits_cosine_sql_and_maps_rows():
    rows = [
        ("RULE-01", "alpha rule text", {"k": "v"}, 0.91),
        ("RULE-02", "beta rule text", '{"j": "w"}', 0.42),
    ]
    conn = FakeConnection(rows=rows)
    store = PgVectorStore(conn, MockEmbeddingProvider(dimensions=8))

    results = store.search(VectorSearchQuery(text="find rule", top_k=2))

    sql_text = " ".join(sql for sql, _ in conn.calls)
    assert "<=>" in sql_text
    assert "LIMIT" in sql_text

    assert len(results) == 2
    assert all(isinstance(r, RetrievedSnippet) for r in results)
    assert results[0].source_id == "RULE-01"
    assert results[0].text == "alpha rule text"
    assert results[0].score == pytest.approx(0.91)
    # The metadata supplied as a JSON string is parsed back into a dict.
    assert results[1].metadata == {"j": "w"}


def test_search_clamps_scores_into_unit_range():
    rows = [("RULE-01", "text one", {}, 1.4), ("RULE-02", "text two", {}, -0.3)]
    conn = FakeConnection(rows=rows)
    store = PgVectorStore(conn, MockEmbeddingProvider(dimensions=8))
    results = store.search(VectorSearchQuery(text="q", top_k=2))
    assert results[0].score == pytest.approx(1.0)
    assert results[1].score == pytest.approx(0.0)


def test_count_returns_int_from_row():
    conn = FakeConnection(rows=[(3,)])
    store = PgVectorStore(conn, MockEmbeddingProvider(dimensions=8))
    assert store.count() == 3


def test_vector_to_pgvector_is_stable_string():
    assert _vector_to_pgvector([0.0, 1.0, 2.5]) == "[0.0,1.0,2.5]"


def test_pgvector_store_satisfies_protocol():
    store = PgVectorStore(FakeConnection(), MockEmbeddingProvider())
    assert isinstance(store, VectorStore)


def test_pgvector_store_has_no_forbidden_domain_terms():
    path = (
        Path(__file__).resolve().parents[1]
        / "src" / "ai_ops_workflow" / "retrieval" / "pgvector_store.py"
    )
    text = path.read_text(encoding="utf-8").lower()
    # Domain terms are forbidden; DB terms (postgres/pgvector) are allowed here.
    for term in ("quarry", "aggregate", "gravel", "tonnes", "kruusakarjaar"):
        assert term not in text, f"forbidden domain term '{term}' found"
