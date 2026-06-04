# Claims map

This maps portfolio and sales claims to the phase that actually earns them. The
discipline is the same as a careful CV: never claim a capability the completed
work does not support. Each component is tagged with the tier at which its
claim becomes true.

## The three tiers

- **Tier 1 (after Phase 0, current):** architecture and design claims. The
  design exists, documented and scaffolded. Nothing runs yet.
- **Tier 2 (after Phase 1 implementation):** working-software claims. The core
  runs end to end with real LLM, real retrieval, and the real graph, locally.
- **Tier 3 (after Phase 3 deploy and demo usage):** deployed and demonstrated
  claims. There is a running instance and an actual demonstrated workflow.

A Tier 2 claim must not be made while only Phase 0 is complete, and a Tier 3
claim must not be made while only Phase 1 is complete.

## Tier 1: claimable now (Phase 0 complete)

These are true today, because the architecture and scaffold exist.

- "Designed a configurable, domain-agnostic AI operations workflow
  architecture using LangGraph, pgvector, Pydantic v2, and Docker."
- "Specified a provider-adapter LLM layer that supports Anthropic, OpenAI,
  local, and mock providers without changing core workflow logic."
- "Defined a core vs config separation so a new client or domain is added as
  configuration, not code."
- "Designed a human-in-the-loop decision flow with confidence-based escalation
  and a full audit trail."
- "Documented a synthetic-data-only privacy model that keeps real client data
  out of the public repository."

What Tier 1 must NOT say: that anything runs, extracts, retrieves, or is
deployed. It is design and scaffold.

## Tier 2: claimable after Phase 1 (MVP working locally)

These become true once the MVP runs end to end.

- "Built a working LangGraph workflow with live LLM extraction validated by
  Pydantic v2 and pgvector retrieval with source citations."
- "Implemented a 4-node decision flow (intake, extract, retrieve, decide or
  escalate) with confidence-based human-in-the-loop escalation."
- "Implemented a provider-adapter LLM layer with a real Anthropic provider and
  a deterministic mock provider for testing."
- "Produced a complete per-run audit log capturing input, extracted fields,
  retrieved context with sources, decision, reasoning, and confidence."
- "Containerised the app with Docker Compose, running the full flow against a
  pgvector-enabled Postgres locally."

What Tier 2 must NOT say: that it is deployed, hosted, used by anyone, or proven
on a real client workflow.

## Tier 3: claimable only after Phase 3 (deployed and demonstrated)

These require a running, demonstrated instance.

- "Deployed a working demo to Fly.io with a public URL."
- "Demonstrated an end-to-end operations decision workflow on synthetic data
  through a web UI."
- "Integrated escalations with Slack."
- Only with a genuine engagement and explicit permission, and only describing
  what truly happened: "Adapted the starter to a real client workflow via a
  private config." Real client usage is never claimed from synthetic demo work.

## Per-component tier table

| Component                         | Phase 0 (design) | Phase 1 (works locally) | Phase 3 (deployed) |
| --------------------------------- | ---------------- | ----------------------- | ------------------ |
| Overall architecture              | Tier 1           | Tier 2                  | Tier 3             |
| LangGraph 4-node flow             | Tier 1 (designed)| Tier 2 (runs)           | Tier 3 (demoed)    |
| LLM provider-adapter layer        | Tier 1 (designed)| Tier 2 (Anthropic+mock) | Tier 3             |
| Live LLM extraction + Pydantic    | Tier 1 (designed)| Tier 2 (real call)      | Tier 3             |
| pgvector retrieval + citations    | Tier 1 (designed)| Tier 2 (real query)     | Tier 3             |
| Escalation / human-in-the-loop    | Tier 1 (designed)| Tier 2 (runs)           | Tier 3             |
| Audit log                         | Tier 1 (designed)| Tier 2 (written)        | Tier 3             |
| Core vs config separation         | Tier 1           | Tier 2 (proven by demo) | Tier 3             |
| Docker deploy                     | Tier 1 (Dockerfile planned) | Tier 2 (compose runs) | Tier 3 (hosted) |
| Fly.io hosted URL                 | not yet          | not yet                 | Tier 3             |
| UI                                | not yet          | not yet                 | Tier 3             |
| SaaS (Slack) integration          | not yet          | not yet                 | Tier 3             |
| Second domain config              | not yet          | not yet (Phase 2)       | Tier 3             |

## Current honest status line

As of Phase 0: "Designed and scaffolded a configurable AI operations workflow
(LangGraph, pgvector, Pydantic v2, Docker) with a provider-adapter LLM layer
and a synthetic demo config. Implementation is the next phase." Nothing is
described as running, deployed, or client-used, because it is not.
