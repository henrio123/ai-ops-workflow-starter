"""Deterministic, offline mock providers (Phase 1 component 2).

These implement the `LLMProvider` and `EmbeddingProvider` protocols without any
network call, vendor SDK, or randomness. They let the graph, retrieval, and
audit be exercised in tests reproducibly and at no cost. Same input always
yields the same output, including across Python runs.
"""

from __future__ import annotations

import hashlib
import types
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel

from .base import EmbeddingResult, ExtractionResult, LLMResponse

# Sentinel marking a field that should be omitted so its schema default applies.
_OMIT = object()


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    """Return (inner_type, is_optional) by stripping a trailing None union."""

    origin = get_origin(annotation)
    if origin is Union or origin is types.UnionType:
        args = get_args(annotation)
        non_none = [arg for arg in args if arg is not type(None)]
        is_optional = len(non_none) != len(args)
        if len(non_none) == 1:
            return non_none[0], is_optional
        return annotation, is_optional
    return annotation, False


def _mock_value(field_name: str, annotation: Any, required: bool) -> Any:
    """Build a deterministic, schema-valid value for one field.

    Supported types map to fixed values. Unsupported optional fields become
    None; unsupported non-required fields are omitted so their default applies;
    unsupported required fields raise ValueError naming the field and type.
    """

    inner, is_optional = _unwrap_optional(annotation)
    origin = get_origin(inner)

    if inner is str:
        return f"mock_{field_name}"
    if inner is bool:
        return True
    if inner is int:
        return 1
    if inner is float:
        return 1.0
    if inner is list or origin is list:
        return []
    if inner is dict or origin is dict:
        return {}

    if is_optional:
        return None
    if not required:
        return _OMIT
    raise ValueError(
        f"MockLLMProvider cannot build a value for required field "
        f"'{field_name}' of unsupported type {inner!r}"
    )


class MockLLMProvider:
    """Deterministic stand-in for a completion and extraction provider."""

    def __init__(self, model: str = "mock-llm", provider: str = "mock") -> None:
        self.model = model
        self.provider = provider

    def complete(self, prompt: str, *, system: str | None = None) -> LLMResponse:
        text = f"MOCK_COMPLETION: {prompt[:80]}"
        usage = {
            "prompt_tokens": len(prompt.split()),
            "completion_tokens": len(text.split()),
        }
        return LLMResponse(
            text=text, model=self.model, provider=self.provider, usage=usage
        )

    def extract(
        self, prompt: str, schema: type[BaseModel], *, system: str | None = None
    ) -> ExtractionResult:
        data: dict[str, Any] = {}
        for field_name, field_info in schema.model_fields.items():
            value = _mock_value(
                field_name, field_info.annotation, field_info.is_required()
            )
            if value is _OMIT:
                continue
            data[field_name] = value

        instance = schema.model_validate(data)
        return ExtractionResult(
            data=instance,
            confidence=0.99,
            raw_text="mock extraction",
            model=self.model,
            provider=self.provider,
        )


class MockEmbeddingProvider:
    """Deterministic stand-in for an embedding provider."""

    def __init__(
        self,
        model: str = "mock-embedding",
        provider: str = "mock",
        dimensions: int = 8,
    ) -> None:
        self.model = model
        self.provider = provider
        self._dimensions = dimensions

    @property
    def dimension(self) -> int:
        return self._dimensions

    def _vector(self, text: str) -> list[float]:
        """Expand a hash of `text` into a stable vector of floats in 0..1."""

        vector: list[float] = []
        counter = 0
        while len(vector) < self._dimensions:
            digest = hashlib.sha256(f"{counter}:{text}".encode("utf-8")).digest()
            for byte in digest:
                vector.append(byte / 255.0)
                if len(vector) >= self._dimensions:
                    break
            counter += 1
        return vector

    def embed(self, texts: list[str]) -> EmbeddingResult:
        if not texts:
            raise ValueError("texts must be a non-empty list")
        for index, text in enumerate(texts):
            if not text or not text.strip():
                raise ValueError(f"text at index {index} must be non-empty")

        embeddings = [self._vector(text) for text in texts]
        return EmbeddingResult(
            embeddings=embeddings, model=self.model, provider=self.provider
        )
