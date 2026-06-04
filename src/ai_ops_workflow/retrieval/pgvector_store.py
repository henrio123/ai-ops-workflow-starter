"""Real pgvector backend implementing the same VectorStore protocol (3b).

This is the database-backed counterpart to the in-memory store from component
3a. It satisfies the identical VectorStore protocol, so it is a drop-in swap for
InMemoryVectorStore. The connection is injected and is never opened here, so this
module imports cleanly even when psycopg is not installed: nothing at module load
touches the driver. Snippets live in a pgvector VECTOR column and search ranks by
the cosine-distance operator (`<=>`), converted to a 0..1 similarity so results
match the in-memory store's semantics (higher means more similar). The table name
is validated as a SQL identifier because it is interpolated into the DDL and DML.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ..core.models import RetrievedSnippet
from ..llm.base import EmbeddingProvider
from .vectorstore import SnippetToIndex, VectorSearchQuery, _validate_vector_dimension

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(name: str) -> str:
    """Return `name` if it is a safe SQL identifier, else raise ValueError.

    The table name is interpolated directly into SQL (identifiers cannot be
    passed as bound parameters), so it must match a strict allowlist.
    """

    if not _IDENTIFIER_RE.match(name):
        raise ValueError(
            f"invalid SQL identifier {name!r}: must match [A-Za-z_][A-Za-z0-9_]*"
        )
    return name


def _vector_to_pgvector(vector: list[float]) -> str:
    """Render a float vector as a pgvector literal like '[0.1,0.2,0.3]'."""

    return "[" + ",".join(str(float(x)) for x in vector) + "]"


def _commit_if_supported(connection: Any) -> None:
    """Commit the connection if it exposes a commit() method."""

    if hasattr(connection, "commit"):
        connection.commit()


def _row_to_retrieved_snippet(row: Any) -> RetrievedSnippet:
    """Map a (source_id, text, metadata, score) row to a RetrievedSnippet."""

    source_id, text, metadata, score = row[0], row[1], row[2], row[3]
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    score = max(0.0, min(1.0, float(score)))
    return RetrievedSnippet(
        source_id=source_id,
        text=text,
        score=score,
        metadata=metadata or {},
    )


class PgVectorStore:
    """pgvector-backed VectorStore. Connection injected, never opened here."""

    def __init__(
        self,
        connection: Any,
        embedding_provider: EmbeddingProvider,
        table_name: str = "policy_snippets",
    ) -> None:
        self.connection = connection
        self.embedding_provider = embedding_provider
        self.table_name = _validate_identifier(table_name)

    def ensure_schema(self) -> None:
        """Create the vector extension and snippet table if they do not exist."""

        dimension = int(self.embedding_provider.dimension)
        with self.connection.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {self.table_name} ("
                "source_id TEXT PRIMARY KEY, "
                "text TEXT NOT NULL, "
                "metadata JSONB NOT NULL DEFAULT '{}'::jsonb, "
                f"embedding VECTOR({dimension}) NOT NULL)"
            )
        _commit_if_supported(self.connection)

    def upsert_snippets(self, snippets: list[SnippetToIndex]) -> int:
        if not snippets:
            raise ValueError("snippets must be a non-empty list")

        embeddings = self.embedding_provider.embed(
            [snippet.text for snippet in snippets]
        ).embeddings
        if len(embeddings) != len(snippets):
            raise ValueError(
                f"embedding count {len(embeddings)} does not match "
                f"snippet count {len(snippets)}"
            )

        expected = self.embedding_provider.dimension
        for vector in embeddings:
            _validate_vector_dimension(vector, expected)

        with self.connection.cursor() as cur:
            for snippet, vector in zip(snippets, embeddings):
                cur.execute(
                    f"INSERT INTO {self.table_name} "
                    "(source_id, text, metadata, embedding) "
                    "VALUES (%s, %s, %s, %s::vector) "
                    "ON CONFLICT (source_id) DO UPDATE SET "
                    "text = EXCLUDED.text, "
                    "metadata = EXCLUDED.metadata, "
                    "embedding = EXCLUDED.embedding",
                    (
                        snippet.source_id,
                        snippet.text,
                        json.dumps(snippet.metadata),
                        _vector_to_pgvector(vector),
                    ),
                )
        _commit_if_supported(self.connection)
        return len(snippets)

    def search(self, query: VectorSearchQuery) -> list[RetrievedSnippet]:
        query_vec = self.embedding_provider.embed([query.text]).embeddings[0]
        _validate_vector_dimension(query_vec, self.embedding_provider.dimension)

        query_literal = _vector_to_pgvector(query_vec)
        with self.connection.cursor() as cur:
            cur.execute(
                "SELECT source_id, text, metadata, "
                "1 - (embedding <=> %s::vector) AS score "
                f"FROM {self.table_name} "
                "ORDER BY embedding <=> %s::vector "
                "LIMIT %s",
                (query_literal, query_literal, query.top_k),
            )
            rows = cur.fetchall()
        return [_row_to_retrieved_snippet(row) for row in rows]

    def count(self) -> int:
        with self.connection.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            row = cur.fetchone()
        return int(row[0])
