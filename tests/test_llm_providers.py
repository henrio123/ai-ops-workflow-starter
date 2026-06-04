"""Tests for the provider-adapter LLM layer (Phase 1 component 2).

All deterministic and offline: no network, no LLM, no spend, no vendor SDK.
"""

from __future__ import annotations

from typing import Optional

import pytest
from pydantic import BaseModel, ValidationError

from ai_ops_workflow.llm import (
    EmbeddingProvider,
    EmbeddingResult,
    ExtractionResult,
    LLMProvider,
    LLMResponse,
    MockEmbeddingProvider,
    MockLLMProvider,
    get_embedding_provider,
    get_llm_provider,
)


class SampleSchema(BaseModel):
    name: str
    count: int
    ratio: float
    active: bool
    tags: list[str]
    meta: dict[str, str]
    note: Optional[str] = None


class CustomType:
    """A non-trivial type the mock cannot synthesize."""


class UnsupportedSchema(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    widget: CustomType


def test_complete_returns_llm_response_with_expected_identity():
    provider = MockLLMProvider()
    response = provider.complete("hello world")
    assert isinstance(response, LLMResponse)
    assert response.provider == "mock"
    assert response.model == "mock-llm"
    assert response.text


def test_complete_is_deterministic():
    provider = MockLLMProvider()
    first = provider.complete("same prompt")
    second = provider.complete("same prompt")
    assert first.text == second.text


def test_extract_builds_valid_instance_for_mixed_field_types():
    provider = MockLLMProvider()
    result = provider.extract("extract this", SampleSchema)
    assert isinstance(result, ExtractionResult)
    assert isinstance(result.data, SampleSchema)
    assert 0.0 <= result.confidence <= 1.0
    assert result.raw_text
    assert result.model == "mock-llm"
    assert result.provider == "mock"


def test_extract_raises_for_unsupported_required_field_type():
    provider = MockLLMProvider()
    with pytest.raises(ValueError):
        provider.extract("extract this", UnsupportedSchema)


def test_embed_returns_one_vector_per_text():
    provider = MockEmbeddingProvider(dimensions=8)
    result = provider.embed(["a", "b", "c"])
    assert isinstance(result, EmbeddingResult)
    assert len(result.embeddings) == 3
    for vector in result.embeddings:
        assert len(vector) == 8
        assert all(isinstance(value, float) for value in vector)
        assert all(0.0 <= value <= 1.0 for value in vector)


def test_embed_is_deterministic():
    provider = MockEmbeddingProvider()
    first = provider.embed(["stable text"]).embeddings[0]
    second = provider.embed(["stable text"]).embeddings[0]
    assert first == second


def test_embed_distinct_texts_generally_differ():
    provider = MockEmbeddingProvider()
    a = provider.embed(["alpha"]).embeddings[0]
    b = provider.embed(["beta"]).embeddings[0]
    assert a != b


def test_embedding_dimension_matches_configuration():
    provider = MockEmbeddingProvider(dimensions=16)
    assert provider.dimension == 16
    assert len(provider.embed(["x"]).embeddings[0]) == 16


def test_embed_rejects_empty_list():
    provider = MockEmbeddingProvider()
    with pytest.raises(ValueError):
        provider.embed([])


def test_embed_rejects_blank_text():
    provider = MockEmbeddingProvider()
    with pytest.raises(ValueError):
        provider.embed(["ok", "   "])


def test_mocks_satisfy_runtime_checkable_protocols():
    assert isinstance(MockLLMProvider(), LLMProvider)
    assert isinstance(MockEmbeddingProvider(), EmbeddingProvider)


def test_factory_returns_mock_providers():
    assert isinstance(get_llm_provider("mock"), MockLLMProvider)
    assert isinstance(get_embedding_provider("mock"), MockEmbeddingProvider)


def test_factory_rejects_unknown_names():
    with pytest.raises(ValueError):
        get_llm_provider("bogus")
    with pytest.raises(ValueError):
        get_embedding_provider("bogus")


def test_llm_response_rejects_empty_required_strings():
    with pytest.raises(ValidationError):
        LLMResponse(text="", model="m", provider="p")
    with pytest.raises(ValidationError):
        LLMResponse(text="t", model="", provider="p")
    with pytest.raises(ValidationError):
        LLMResponse(text="t", model="m", provider="")


def test_extraction_result_rejects_bad_fields():
    instance = SampleSchema(
        name="x", count=1, ratio=1.0, active=True, tags=[], meta={}
    )
    with pytest.raises(ValidationError):
        ExtractionResult(
            data=instance,
            confidence=1.5,
            raw_text="r",
            model="m",
            provider="p",
        )
    with pytest.raises(ValidationError):
        ExtractionResult(
            data=instance,
            confidence=0.5,
            raw_text="",
            model="m",
            provider="p",
        )


def test_embedding_result_rejects_empty_embeddings_and_vectors():
    with pytest.raises(ValidationError):
        EmbeddingResult(embeddings=[], model="m", provider="p")
    with pytest.raises(ValidationError):
        EmbeddingResult(embeddings=[[]], model="m", provider="p")
