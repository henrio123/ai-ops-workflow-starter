"""Graph state schema (Phase 0 placeholder).

Defines the typed state that flows through the LangGraph nodes. All fields are
generic; no domain meaning lives here. Domain field shapes arrive via the
config's Pydantic extraction schema and are carried in `extracted` as an opaque
validated model.

Planned shape (illustrative, implemented in Phase 1):

    class WorkflowState(TypedDict, total=False):
        request_id: str
        config_name: str
        raw_input: str | dict          # normalised request or document
        metadata: dict                 # timestamps, document type, source
        extracted: BaseModel | None    # validated against config schema
        extraction_confidence: float
        retrieved: list[RetrievedSnippet]  # snippet text + source citation
        decision: Decision | None
        escalated: bool
        reasoning: str
        audit: list[AuditEntry]

No logic in Phase 0.
"""
