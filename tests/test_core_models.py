"""Tests for core domain-agnostic models and state (Phase 1 component 1).

These run with no network and no LLM. They cover validation invariants, JSON
serialization, the escalation flag rule, and the domain-neutrality of core.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_ops_workflow.core.models import (
    AuditEntry,
    AuditEvent,
    Citation,
    Decision,
    Outcome,
    RetrievedSnippet,
    WorkflowResult,
)
from ai_ops_workflow.core.state import make_initial_state


def test_retrieved_snippet_validates_and_serializes():
    snippet = RetrievedSnippet(source_id="RULE-03", text="some rule text", score=0.5)
    dumped = snippet.model_dump(mode="json")
    assert dumped["source_id"] == "RULE-03"
    assert dumped["text"] == "some rule text"
    assert dumped["score"] == 0.5
    assert dumped["metadata"] == {}


def test_retrieved_snippet_rejects_empty_source_id():
    with pytest.raises(ValidationError):
        RetrievedSnippet(source_id="", text="text")


def test_retrieved_snippet_rejects_empty_text():
    with pytest.raises(ValidationError):
        RetrievedSnippet(source_id="X-1", text="   ")


@pytest.mark.parametrize("bad_score", [-0.1, 1.1])
def test_retrieved_snippet_rejects_score_out_of_range(bad_score):
    with pytest.raises(ValidationError):
        RetrievedSnippet(source_id="X-1", text="text", score=bad_score)


def test_decision_escalate_requires_escalation_flag_true():
    with pytest.raises(ValidationError):
        Decision(
            outcome=Outcome.escalate,
            reasoning="needs human review",
            confidence=0.4,
            escalation_flag=False,
        )


def test_decision_escalate_with_flag_true_is_valid():
    decision = Decision(
        outcome=Outcome.escalate,
        reasoning="needs human review",
        confidence=0.4,
        escalation_flag=True,
    )
    assert decision.outcome is Outcome.escalate
    assert decision.escalation_flag is True


@pytest.mark.parametrize("bad_confidence", [-0.01, 1.01])
def test_decision_rejects_confidence_out_of_range(bad_confidence):
    with pytest.raises(ValidationError):
        Decision(
            outcome=Outcome.confirm,
            reasoning="ok",
            confidence=bad_confidence,
            escalation_flag=False,
        )


def test_workflow_result_is_json_serializable_with_string_outcome():
    result = WorkflowResult(
        request_id="req-1",
        config_name="test_config",
        outcome=Outcome.escalate,
        reasoning="needs human review",
        confidence=0.42,
        citations=[Citation(source_id="RULE-03")],
        escalation_flag=True,
        audit_reference="audit-1",
    )
    payload = json.loads(json.dumps(result.model_dump(mode="json")))
    for key in (
        "request_id",
        "config_name",
        "outcome",
        "reasoning",
        "confidence",
        "citations",
        "escalation_flag",
        "audit_reference",
    ):
        assert key in payload
    assert payload["outcome"] == "escalate"
    assert isinstance(payload["outcome"], str)


def test_workflow_result_escalate_requires_escalation_flag_true():
    with pytest.raises(ValidationError):
        WorkflowResult(
            request_id="req-1",
            config_name="test_config",
            outcome=Outcome.escalate,
            reasoning="needs human review",
            confidence=0.42,
            escalation_flag=False,
            audit_reference="audit-1",
        )


def test_audit_event_has_datetime_timestamp():
    event = AuditEvent(event_type="extract", message="extracted fields")
    assert isinstance(event.timestamp, datetime)
    assert event.timestamp is not None
    assert event.timestamp.tzinfo is not None
    assert event.timestamp.utcoffset() is not None


def test_audit_entry_defaults_events_to_list():
    entry = AuditEntry(request_id="req-1", node_name="extract")
    assert entry.events == []
    assert isinstance(entry.events, list)


def test_make_initial_state_returns_domain_neutral_keys():
    state = make_initial_state(
        request_id="req-1",
        config_name="test_config",
        raw_input="some request text",
    )
    assert state["request_id"] == "req-1"
    assert state["config_name"] == "test_config"
    assert state["raw_input"] == "some request text"
    assert state["document_type"] is None
    assert state["extracted"] is None
    assert state["extraction_confidence"] is None
    assert state["retrieved_snippets"] == []
    assert state["decision"] is None
    assert state["result"] is None
    assert state["audit_entries"] == []
    assert state["errors"] == []


@pytest.mark.parametrize(
    "kwargs",
    [
        {"request_id": "", "config_name": "c", "raw_input": "r"},
        {"request_id": "req", "config_name": "  ", "raw_input": "r"},
        {"request_id": "req", "config_name": "c", "raw_input": ""},
    ],
)
def test_make_initial_state_rejects_empty_required_fields(kwargs):
    with pytest.raises(ValueError):
        make_initial_state(**kwargs)


def test_core_contains_no_demo_specific_terms():
    repo_root = Path(__file__).resolve().parents[1]
    core_dir = repo_root / "src" / "ai_ops_workflow" / "core"
    forbidden = ("quarry", "aggregate", "gravel", "tonnes", "kruusakarjaar")
    py_files = list(core_dir.glob("*.py")) + list((core_dir / "nodes").glob("*.py"))
    assert py_files, "expected core python files to scan"
    for path in py_files:
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden:
            assert term not in text, f"demo-specific term '{term}' found in {path}"
