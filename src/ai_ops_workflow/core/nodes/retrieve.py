"""Retrieve node (Phase 0 placeholder).

Embeds the extracted fields or the request text and queries the pgvector store
for the top-k most similar policy and rule snippets, returning each with its
source citation. Retrieval is generic; the snippets table and the config's
retrieval settings (top_k, embedding model, similarity metric) supply the
specifics.

Planned signature (Phase 1):

    def retrieve(state: WorkflowState, config: WorkflowConfig,
                 store: VectorStore, embedder: Embedder) -> WorkflowState: ...

Writes an audit entry recording which snippets and sources were retrieved.

No logic in Phase 0.
"""
