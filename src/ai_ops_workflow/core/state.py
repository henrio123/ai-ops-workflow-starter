"""Graph state for the workflow (Phase 1 component 1).

WorkflowState is the typed, domain-neutral state that flows through the graph.
No domain meaning lives here: the keys are generic. The extractor's
domain-specific output is carried in `extracted` as an opaque model, so the
core never depends on any client's field shapes.

This module defines no logic beyond a small constructor for the initial state.
No external calls, no domain logic.
"""

from __future__ import annotations

from typing import Any, TypedDict

from .models import AuditEntry, Decision, RetrievedSnippet, WorkflowResult


class WorkflowState(TypedDict, total=False):
    """Generic state passed between nodes.

    All keys are optional (total=False). Domain field shapes are held in
    `extracted` as an opaque, separately validated model; the core treats it as
    Any so no domain type leaks into the engine.
    """

    request_id: str
    config_name: str
    raw_input: str
    document_type: str | None
    extracted: Any
    extraction_confidence: float | None
    retrieved_snippets: list[RetrievedSnippet]
    decision: Decision | None
    result: WorkflowResult | None
    audit_entries: list[AuditEntry]
    errors: list[str]


def make_initial_state(
    request_id: str,
    config_name: str,
    raw_input: str,
    document_type: str | None = None,
) -> WorkflowState:
    """Build the initial WorkflowState for a run.

    Validates that request_id, config_name, and raw_input are non-empty.
    Initializes the list keys to empty lists and decision and result to None.
    No domain logic and no external calls.
    """

    for name, value in (
        ("request_id", request_id),
        ("config_name", config_name),
        ("raw_input", raw_input),
    ):
        if not value or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    state: WorkflowState = {
        "request_id": request_id,
        "config_name": config_name,
        "raw_input": raw_input,
        "document_type": document_type,
        "extracted": None,
        "extraction_confidence": None,
        "retrieved_snippets": [],
        "decision": None,
        "result": None,
        "audit_entries": [],
        "errors": [],
    }
    return state
