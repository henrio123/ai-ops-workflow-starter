"""pgvector store (Phase 0 placeholder).

Wraps a Postgres table with a pgvector column holding policy and rule snippet
embeddings alongside the snippet text, a source id, and a version. Keeping
embeddings next to relational data means a top-k query returns the snippet and
its citation together, and the audit log can record exactly which rows were
used.

Planned shape (illustrative, implemented in Phase 1):

    class VectorStore:
        def upsert(self, snippets: list[Snippet]) -> None: ...
        def search(self, query_vector: list[float], top_k: int
                   ) -> list[RetrievedSnippet]: ...   # cosine similarity

    # Table sketch:
    #   policy_snippets(id, source_id, text, version, embedding vector(N))

No DB connection, no SQL execution, no logic in Phase 0.
"""
