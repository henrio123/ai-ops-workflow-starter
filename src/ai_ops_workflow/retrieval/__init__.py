"""Retrieval layer (pgvector).

Domain-agnostic. Stores policy and rule snippets with their embeddings and
source ids in a pgvector table, and runs top-k similarity queries that return
snippets together with citations. The embedder comes from the LLM layer so this
package stays vendor-neutral.

Phase 0: placeholder modules only.
"""
