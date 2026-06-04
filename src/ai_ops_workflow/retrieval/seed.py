"""Snippet seeding (placeholder; needs the config component, not in 3a).

Reads a config's rules source, splits it into snippets with source ids, embeds
them through the EmbeddingProvider, and upserts them into the vector store.
Seeding is generic; the source text and ids are supplied by the config.

Planned shape:

    def seed_from_config(config: WorkflowConfig, store: VectorStore,
                         embedding_provider: EmbeddingProvider) -> int:
        # returns number of snippets seeded
        ...

No file parsing, no embedding, no logic here yet. This module imports nothing
database-related.
"""
