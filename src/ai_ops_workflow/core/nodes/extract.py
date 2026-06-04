"""Extract node (Phase 0 placeholder).

Calls the LLM through the LLMProvider interface to pull structured fields from
the normalised request, then validates them against the config's Pydantic v2
extraction schema. Produces typed fields plus an extraction confidence. On
validation failure, signals a retry or lowered confidence rather than crashing.

This node is where free text becomes typed data. It never imports a vendor SDK
directly; it depends only on the injected LLMProvider.

Planned signature (Phase 1):

    def extract(state: WorkflowState, config: WorkflowConfig,
                provider: LLMProvider) -> WorkflowState: ...

Writes an audit entry with the extracted fields and confidence.

No logic in Phase 0.
"""
