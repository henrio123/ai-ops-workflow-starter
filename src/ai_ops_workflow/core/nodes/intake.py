"""Intake node (Phase 0 placeholder).

Receives a raw operational request or document, validates its document type
against the config, attaches metadata (request_id, config_name, source,
document type), and normalises it into WorkflowState. No domain logic; the
allowed document types come from the config.

Planned signature (Phase 1):

    def intake(state: WorkflowState, config: WorkflowConfig) -> WorkflowState: ...

Writes an audit entry for the intake step.

No logic in Phase 0.
"""
