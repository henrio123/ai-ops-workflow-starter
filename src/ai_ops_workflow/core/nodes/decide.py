"""Decide or escalate node (Phase 0 placeholder).

Applies the config's decision policy to the extracted fields and retrieved
rules. Enforces escalation uniformly: if confidence is below the config's
min_confidence, or an always-escalate rule trigger fires, the outcome is
escalation to a human rather than an auto-decision. Otherwise it emits a
recommended decision with reasoning and the cited source ids.

A conditional edge after this node selects the output assembly path
(decision vs escalation). Escalation is a first-class outcome, not an error.

Planned signature (Phase 1):

    def decide(state: WorkflowState, config: WorkflowConfig,
               provider: LLMProvider) -> WorkflowState: ...

Writes an audit entry with the decision or escalation, reasoning, confidence,
and citations.

No logic in Phase 0.
"""
