"""Base Pydantic v2 models shared by the core (Phase 0 placeholder).

These are domain-agnostic building blocks. Domain extraction schemas live in
each config's schemas.py and are not defined here.

Planned models (illustrative, implemented in Phase 1):

    class RetrievedSnippet(BaseModel):
        source_id: str        # e.g. "CREDIT-03", used for citation
        text: str
        score: float          # similarity score

    class Decision(BaseModel):
        outcome: str          # config-defined, e.g. confirm | revise | escalate
        reasoning: str
        confidence: float
        citations: list[str]  # source_ids that justified the decision

    class EscalationThresholds(BaseModel):
        min_confidence: float
        always_escalate_when: list[dict]

    class WorkflowResult(BaseModel):
        request_id: str
        decision: Decision | None
        escalated: bool
        citations: list[RetrievedSnippet]

No logic in Phase 0.
"""
