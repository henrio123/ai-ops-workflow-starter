"""Core domain-agnostic models (Phase 1 component 1).

Real, typed building blocks for the workflow engine. These types carry no
domain meaning: no client or industry concept appears here. Domain specifics
live in each config (see configs/), never in the core. The extractor's domain
output is carried elsewhere as an opaque validated model; the types below are
the generic contract the engine and the audit log speak.

Pydantic v2 idioms are used throughout: Field with descriptions, field and
model validators for invariants, and default_factory for mutable defaults.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Outcome(str, Enum):
    """Generic decision outcomes.

    Subclasses str so it serializes to its plain string value in JSON. The core
    defines a small generic outcome set; each config decides which outcomes it
    uses.
    """

    confirm = "confirm"
    revise = "revise"
    escalate = "escalate"
    reject = "reject"


class RetrievedSnippet(BaseModel):
    """A policy or rule snippet returned by retrieval, with its citation key."""

    source_id: str = Field(description="Citation key identifying the snippet source.")
    text: str = Field(description="The snippet text retrieved from the store.")
    score: float | None = Field(
        default=None, description="Optional similarity score in the range 0..1."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional free-form snippet metadata."
    )

    @field_validator("source_id", "text")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value

    @field_validator("score")
    @classmethod
    def _score_in_range(cls, value: float | None) -> float | None:
        if value is not None and not (0.0 <= value <= 1.0):
            raise ValueError("score must be in the range 0..1")
        return value


class Citation(BaseModel):
    """A reference to a source that justified a decision."""

    source_id: str = Field(description="Citation key identifying the cited source.")
    quote: str | None = Field(
        default=None, description="Optional quoted text supporting the citation."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Optional free-form citation metadata."
    )

    @field_validator("source_id")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value


class Decision(BaseModel):
    """A recommended decision produced by the decide step."""

    outcome: Outcome = Field(description="The recommended generic outcome.")
    reasoning: str = Field(description="Human-readable rationale for the outcome.")
    confidence: float = Field(description="Confidence in the outcome, in 0..1.")
    citations: list[Citation] = Field(
        default_factory=list, description="Sources that justified the outcome."
    )
    escalation_flag: bool = Field(
        description="True when the case is routed to a human instead of decided."
    )

    @field_validator("reasoning")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value

    @field_validator("confidence")
    @classmethod
    def _confidence_in_range(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("confidence must be in the range 0..1")
        return value

    @model_validator(mode="after")
    def _escalate_requires_flag(self) -> "Decision":
        if self.outcome is Outcome.escalate and not self.escalation_flag:
            raise ValueError(
                "escalation_flag must be true when outcome is escalate"
            )
        return self


class WorkflowResult(BaseModel):
    """The final, JSON-serializable result of one workflow run."""

    request_id: str = Field(description="Identifier of the originating request.")
    config_name: str = Field(description="Name of the config that handled the run.")
    outcome: Outcome = Field(description="The recommended generic outcome.")
    reasoning: str = Field(description="Human-readable rationale for the outcome.")
    confidence: float = Field(description="Confidence in the outcome, in 0..1.")
    citations: list[Citation] = Field(
        default_factory=list, description="Sources that justified the outcome."
    )
    escalation_flag: bool = Field(
        description="True when the case is routed to a human instead of decided."
    )
    audit_reference: str = Field(
        description="Reference linking this result to its audit record."
    )

    @field_validator("request_id", "config_name", "reasoning", "audit_reference")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value

    @field_validator("confidence")
    @classmethod
    def _confidence_in_range(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("confidence must be in the range 0..1")
        return value

    @model_validator(mode="after")
    def _escalate_requires_flag(self) -> "WorkflowResult":
        if self.outcome is Outcome.escalate and not self.escalation_flag:
            raise ValueError(
                "escalation_flag must be true when outcome is escalate"
            )
        return self


class AuditEvent(BaseModel):
    """A single timestamped event recorded within a node's audit entry."""

    event_type: str = Field(description="Short type tag for the event.")
    message: str = Field(description="Human-readable description of the event.")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC time the event was recorded.",
    )
    data: dict[str, Any] = Field(
        default_factory=dict, description="Optional structured event payload."
    )

    @field_validator("event_type", "message")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value


class AuditEntry(BaseModel):
    """The audit record for one node's execution within a run."""

    request_id: str = Field(description="Identifier of the originating request.")
    node_name: str = Field(description="Name of the node that produced the entry.")
    events: list[AuditEvent] = Field(
        default_factory=list, description="Ordered events recorded by the node."
    )

    @field_validator("request_id", "node_name")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value
