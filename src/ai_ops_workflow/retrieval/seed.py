"""Snippet seeding (Phase 0 placeholder).

Reads a config's rules_source (for example configs/demo_quarry/policies/
rules.md), splits it into snippets with source ids, embeds them through the
EmbeddingProvider, and upserts them into the pgvector store. Seeding is generic; the
source text and ids are supplied by the config.

Planned shape (Phase 1):

    def seed_from_config(config: WorkflowConfig, store: VectorStore,
                         embedding_provider: EmbeddingProvider) -> int:
        # returns number of snippets seeded
        ...

No file parsing, no embedding, no logic in Phase 0.
"""
