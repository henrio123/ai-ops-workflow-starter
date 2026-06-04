"""End-to-end pgvector integration test against a real Postgres (component 3b).

Skipped unless DATABASE_URL is set, so the default offline test run never touches
a database. To run it: bring up docker compose (pgvector/pgvector:pg16), export
DATABASE_URL pointing at it, then `pytest -m integration`. The synthetic snippets
here are domain-neutral on purpose.
"""

from __future__ import annotations

import os

import pytest

psycopg = pytest.importorskip("psycopg")

pytestmark = pytest.mark.integration

if not os.environ.get("DATABASE_URL"):
    pytest.skip(
        "set DATABASE_URL (and run docker compose) to run pgvector integration tests",
        allow_module_level=True,
    )

from ai_ops_workflow.core.models import RetrievedSnippet
from ai_ops_workflow.llm.mock_provider import MockEmbeddingProvider
from ai_ops_workflow.retrieval import PgVectorStore, SnippetToIndex, VectorSearchQuery


def test_pgvector_end_to_end():
    table_name = "test_policy_snippets"
    conn = psycopg.connect(os.environ["DATABASE_URL"])
    try:
        store = PgVectorStore(
            conn, MockEmbeddingProvider(dimensions=8), table_name=table_name
        )
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()

        store.ensure_schema()

        inserted = store.upsert_snippets(
            [
                SnippetToIndex(source_id="RULE-01", text="alpha rule text"),
                SnippetToIndex(source_id="RULE-02", text="beta rule text"),
                SnippetToIndex(source_id="RULE-03", text="gamma rule text"),
            ]
        )
        assert inserted == 3
        assert store.count() == 3

        query = VectorSearchQuery(text="alpha rule text", top_k=2)
        results = store.search(query)
        assert results, "expected at least one result"
        assert len(results) <= query.top_k
        inserted_ids = {"RULE-01", "RULE-02", "RULE-03"}
        for snippet in results:
            assert isinstance(snippet, RetrievedSnippet)
            assert 0.0 <= snippet.score <= 1.0
            assert snippet.source_id in inserted_ids

        # The same query twice yields the same ordering (deterministic).
        again = store.search(query)
        assert [r.source_id for r in again] == [r.source_id for r in results]
    finally:
        with conn.cursor() as cur:
            cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        conn.close()
