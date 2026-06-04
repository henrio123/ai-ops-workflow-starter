# Acceptance criteria

What "MVP done" (end of Phase 1) means, stated as testable conditions. Each is
checkable by running the system or the test suite, not by opinion.

## Definition of MVP done

The MVP is done when a single synthetic request runs end to end through real
machinery, exercising all four gap-closing technologies, and the outcome is
recorded in an audit log.

## Functional criteria

1. **End-to-end run.** Running the CLI against a synthetic `demo_quarry` sample
   produces a result object containing: decision (`confirm`, `revise`, or
   `escalate`), reasoning, confidence, cited context, and an escalation flag.
2. **Live LLM extraction.** The `extract` node makes a real call through the
   `LLMProvider` interface (Anthropic by default) and returns fields that pass
   the config's Pydantic v2 schema. With the mock provider selected, the same
   node runs deterministically with no network call.
3. **pgvector retrieval with citations.** The `retrieve` node returns top-k
   snippets from the pgvector table, each carrying a source id, and at least
   one returned snippet is cited in the output for a decision that depends on a
   rule.
4. **LangGraph 4-node flow.** The graph runs intake to extract to retrieve to
   decide, with a conditional edge that sends low-confidence or rule-triggered
   cases to the escalation output instead of a decision.
5. **Escalation works.** A synthetic sample that trips an escalation rule (for
   example a new customer over the credit volume) yields `escalate` with the
   triggering rule cited, and does not emit a confident auto-decision.
6. **Audit log complete.** For every run, the audit record contains input,
   extracted fields, retrieved context with sources, the decision or
   escalation, reasoning, and confidence. No step is missing.
7. **Dockerized local run.** `docker compose up` brings up the app and a
   pgvector-enabled Postgres locally, and the same end-to-end run succeeds
   inside the containers.

## Quality and safety criteria

8. **Config-driven, no demo-domain logic in core.** Grepping the `core/`,
   `llm/`, and `retrieval/` packages finds no demo-specific terms such as
   `quarry`, `aggregate`, `gravel`, `tonnes`, or `Kruusakarjaar`. Generic
   operational terms such as `request`, `document`, `source`, `customer`, or
   `order` are allowed only if they are domain-neutral.
9. **Provider swap is config or env only.** Switching from the Anthropic
   provider to the mock provider requires no change to any file under `core/`.
10. **Synthetic data only.** No real data anywhere in the repo; `.env` is
    gitignored and only `.env.example` with placeholders is committed.
11. **Validation failure is handled.** When the LLM returns fields that fail
    the Pydantic schema, the system retries or lowers confidence and can
    escalate, rather than crashing.
12. **Structured output contract.** The final result is JSON-serializable and
    follows a typed Pydantic model with fields for `request_id`, `config_name`,
    `outcome`, `reasoning`, `confidence`, `citations`, `escalation_flag`, and
    `audit_reference`.

## Test criteria

13. **Smoke test passes.** A test runs the full graph with the mock provider
    end to end and asserts a well-formed result and a complete audit record.
14. **Escalation test passes.** A test feeds a rule-tripping synthetic sample
    and asserts the outcome is `escalate` with the expected rule cited.
15. **Schema test passes.** A test asserts the extractor output validates
    against `AggregateOrderFields` and that a malformed payload is rejected.
16. **Tests need no network or spend.** The full test suite runs with the mock
    provider and a local or test Postgres, with no real LLM call.

## Out of scope for MVP acceptance

A hosted URL, a UI, multiple configs, a second LLM provider, authentication,
and performance targets are explicitly not required for MVP done. They belong
to Phase 2 and Phase 3.
