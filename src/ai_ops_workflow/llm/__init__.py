"""Provider-adapter LLM layer.

The core depends only on the LLMProvider interface in base.py, never on a vendor
SDK. Implementations (Anthropic by default for Phase 1, plus mock, with OpenAI
and local planned later) can be swapped via config or environment without
changing any core node. Embeddings live here too (Embedder) so retrieval stays
vendor-neutral.

Phase 0: placeholder modules only.
"""
