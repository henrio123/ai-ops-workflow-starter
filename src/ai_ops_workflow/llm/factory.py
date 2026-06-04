"""Provider factory (Phase 0 placeholder).

Resolves which LLMProvider to use from configuration or environment, so the
core never names a vendor. Default planned resolution for Phase 1 is Anthropic;
tests select the mock provider. OpenAI and local providers slot in here later
with no core change.

Planned shape (Phase 1):

    def get_provider(name: str | None = None) -> LLMProvider:
        # name resolved from arg, then env (LLM_PROVIDER), then default
        # "anthropic" -> AnthropicProvider, "mock" -> MockProvider, ...
        ...

No logic in Phase 0.
"""
