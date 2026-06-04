"""Audit log (Phase 0 placeholder).

Cross-cutting concern. Every node appends a structured entry keyed by
request_id so the full chain is reconstructable: input, extracted fields,
retrieved context with sources, decision or escalation, reasoning, confidence.

Planned API (illustrative, implemented in Phase 1):

    class AuditEntry(BaseModel):
        request_id: str
        step: str            # intake | extract | retrieve | decide
        payload: dict        # step-specific record
        # timestamp is stamped by the runtime, not generated in pure code

    class AuditLog:
        def record(self, request_id: str, step: str, payload: dict) -> None: ...
        def entries_for(self, request_id: str) -> list[AuditEntry]: ...

Phase 1 may persist entries to Postgres; Phase 0 defines the contract only.

No logic in Phase 0.
"""
