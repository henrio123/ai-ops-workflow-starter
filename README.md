# ai-ops-workflow-starter

A domain-agnostic architecture and scaffold for a "request or document to
decision" workflow engine. The intended MVP will take an operational request or
document, extract structured fields, retrieve relevant rules and policies, run a
decision flow, and return a recommended decision with reasoning, an escalation
flag, and an audit log.

The core is domain-agnostic. Each client or domain is added as a **config**,
not as new code.

> **Status:** Phase 0 (architecture and scaffold). This repository is
> public-bound and portfolio-oriented. It is **not** deployed, not
> production-ready, and not used with any real client. Only synthetic demo
> data lives here. See [docs/build-phases.md](docs/build-phases.md) for what
> is and is not built yet.

## What the MVP is designed to do

1. **Intake** an operational request or document (synthetic in this repo).
2. **Extract** structured fields from it using a real LLM, validated with
   Pydantic v2.
3. **Retrieve** the relevant policy and rule snippets from a pgvector store
   using embeddings and top-k similarity, keeping source citations.
4. **Decide or escalate** using a LangGraph flow and a config-defined decision
   policy. Low confidence routes to a human instead of deciding blindly.
5. **Output** a recommended decision, reasoning, confidence, the cited
   context, an escalation flag, and a complete audit log.

## Who it is for

- Operations teams that triage repetitive request or document decisions
  (order intake, eligibility checks, claim pre-screening, approvals).
- An AI-implementation portfolio and sales demo: one core, many configs.
- Engineers who want a typed, config-driven starter for retrieval-augmented
  decision workflows rather than a one-off script.

## Core vs config

| Layer        | Lives where                         | Domain-specific? |
| ------------ | ----------------------------------- | ---------------- |
| Workflow core | `src/ai_ops_workflow/core/`        | No               |
| LLM adapters | `src/ai_ops_workflow/llm/`          | No               |
| Retrieval    | `src/ai_ops_workflow/retrieval/`    | No               |
| Client config | `src/ai_ops_workflow/configs/<name>/` | Yes            |

A config declares: document and request types, the Pydantic extraction schema,
the rules and policy source, the decision policy, and the escalation
thresholds. The core never hardcodes a domain. See
[docs/config-schema.md](docs/config-schema.md).

## Tech stack

- **Language:** Python, fully typed, Pydantic v2.
- **Agent flow:** LangGraph, a minimal 4-node graph
  (intake to extract to retrieve to decide or escalate).
- **Vector store:** pgvector on Postgres for policy and rule snippets,
  embeddings, and top-k retrieval with citations.
- **LLM layer:** provider-adapter design. Phase 1 default provider is
  Anthropic. OpenAI, local, and mock providers can be added without changing
  the core workflow.
- **Planned deploy target:** Docker (local containers) plus Fly.io (hosted, Phase 3).
- **Optional later:** a small FastAPI or HTML UI and one SaaS integration
  (for example Slack).

## Honest scope

This is a starter and a demo, not a finished product. Phase 0 is documents and
scaffold only, with no application logic. The demo config uses synthetic data
for a fictional quarry or order workflow ("Demo Kruusakarjaar OU" style). Real
client data must never be committed. See
[docs/data-privacy.md](docs/data-privacy.md).

## Documentation

- [architecture.md](docs/architecture.md) - layers, data flow, why these choices.
- [config-schema.md](docs/config-schema.md) - how a client config is structured.
- [demo-use-case.md](docs/demo-use-case.md) - the synthetic quarry demo config.
- [data-privacy.md](docs/data-privacy.md) - synthetic-only rule and separation.
- [build-phases.md](docs/build-phases.md) - MVP scope and later phases.
- [acceptance-criteria.md](docs/acceptance-criteria.md) - what "MVP done" means.
- [claims-map.md](docs/claims-map.md) - what may be claimed at each phase.

## Repository layout

```
ai-ops-workflow-starter/
├── README.md
├── pyproject.toml          # intended dependencies, listed not installed
├── .env.example
├── docs/                   # all Phase 0 design docs
├── src/ai_ops_workflow/
│   ├── core/               # domain-agnostic workflow (LangGraph, audit)
│   ├── llm/                # provider adapters (anthropic, mock, ...)
│   ├── retrieval/          # pgvector store and embeddings
│   └── configs/demo_quarry/  # one synthetic example config
├── tests/                  # smoke test scaffold
└── docker/                 # Dockerfile and compose for local Postgres
```
