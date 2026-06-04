"""LLM and embedding provider contracts (Phase 1 component 2).

Two sibling protocols are the only LLM contract the core depends on:
`LLMProvider` handles completion and extraction (the chat-style calls), and
`EmbeddingProvider` handles embeddings for retrieval. They are deliberately
distinct, so extraction and embeddings can use different providers and the
retrieval layer depends only on `EmbeddingProvider`, never on `LLMProvider`.

Implementations are swappable behind these protocols, so there is no vendor
lock-in. This module imports no vendor SDK and makes no network call; it defines
only the typed request/result models and the protocols.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LLMResponse(BaseModel):
    """A completion response from an LLM provider."""

    text: str = Field(description="The generated completion text.")
    model: str = Field(description="Identifier of the model that produced the text.")
    provider: str = Field(description="Identifier of the provider adapter used.")
    usage: dict[str, int] = Field(
        default_factory=dict, description="Optional token usage counts."
    )

    @field_validator("text", "model", "provider")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value


class ExtractionResult(BaseModel):
    """A structured extraction result wrapping a validated schema instance."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: BaseModel = Field(description="The validated extracted schema instance.")
    confidence: float = Field(description="Confidence in the extraction, in 0..1.")
    raw_text: str = Field(description="The raw model output the data was parsed from.")
    model: str = Field(description="Identifier of the model that produced the data.")
    provider: str = Field(description="Identifier of the provider adapter used.")

    @field_validator("confidence")
    @classmethod
    def _confidence_in_range(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("confidence must be in the range 0..1")
        return value

    @field_validator("raw_text", "model", "provider")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value


class EmbeddingResult(BaseModel):
    """An embedding response: one vector per input text."""

    embeddings: list[list[float]] = Field(
        description="One embedding vector per input text."
    )
    model: str = Field(description="Identifier of the embedding model used.")
    provider: str = Field(description="Identifier of the provider adapter used.")

    @field_validator("embeddings")
    @classmethod
    def _non_empty_vectors(cls, value: list[list[float]]) -> list[list[float]]:
        if not value:
            raise ValueError("embeddings must be a non-empty list")
        for index, vector in enumerate(value):
            if not vector:
                raise ValueError(f"embedding vector at index {index} must be non-empty")
        return value

    @field_validator("model", "provider")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("must be a non-empty string")
        return value


@runtime_checkable
class LLMProvider(Protocol):
    """Completion and extraction contract. No vendor type appears here."""

    def complete(self, prompt: str, *, system: str | None = None) -> LLMResponse:
        """Return a completion for `prompt`, optionally guided by `system`."""
        ...

    def extract(
        self, prompt: str, schema: type[BaseModel], *, system: str | None = None
    ) -> ExtractionResult:
        """Extract fields from `prompt` into a validated instance of `schema`."""
        ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Embedding contract for retrieval. Independent of `LLMProvider`."""

    def embed(self, texts: list[str]) -> EmbeddingResult:
        """Return one embedding vector per text in `texts`."""
        ...

    @property
    def dimension(self) -> int:
        """Vector length, so the vector store can size its column."""
        ...
