"""Anthropic provider adapter (Phase 0 placeholder).

The default planned provider for Phase 1. Implements the LLMProvider interface
from base.py using the Anthropic SDK. Reads its API key from the environment
(never from a config file). No key is required in Phase 0 because nothing runs.

Planned shape (Phase 1):

    class AnthropicProvider:
        def __init__(self, model: str, api_key_env: str = "ANTHROPIC_API_KEY"): ...
        def complete(self, prompt, *, system=None) -> str: ...
        def extract(self, prompt, schema) -> BaseModel: ...

No SDK import, no network call, no logic in Phase 0.
"""
