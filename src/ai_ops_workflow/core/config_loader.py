"""Config loader and WorkflowConfig contract (Phase 0 placeholder).

The core consumes a single typed WorkflowConfig that supplies all domain
specifics. The loader resolves a config by name from the registry in
configs/__init__.py. The core never inspects domain meaning; it only runs the
schema, the policy, and the thresholds the config provides.

Planned contract (illustrative, implemented in Phase 1):

    class RetrievalSettings(BaseModel):
        top_k: int
        embedding_model: str
        similarity: str

    class WorkflowConfig(BaseModel):
        name: str
        description: str
        document_types: list[str]
        extraction_schema: type[BaseModel]
        extraction_prompt: str
        rules_source: str | list[str]
        decision_policy: Callable[..., Decision]
        decision_prompt: str | None
        escalation_thresholds: EscalationThresholds
        retrieval: RetrievalSettings

    def load_config(name: str) -> WorkflowConfig: ...

See docs/config-schema.md.

No logic in Phase 0.
"""
