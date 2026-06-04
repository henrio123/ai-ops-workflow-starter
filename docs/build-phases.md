# Build phases

This document defines what is built when. Phase 0 is the current phase:
documents and scaffold only. The MVP is Phase 1 and deliberately includes all
four gap-closing technologies from the start, each used minimally rather than
deferred.

## Phase 0: architecture and scaffold (current)

Documents and an empty-but-typed scaffold. **No application logic, no LLM
calls, no installed dependencies, no deploy.**

Deliverables:

- All design docs in `docs/`.
- Directory scaffold with placeholder files (docstrings and comments only).
- `.gitignore`, `.env.example`.
- `pyproject.toml` listing intended dependencies (listed, not installed).
- Local git repository with an initial commit.

Done when: the scaffold and all docs exist, em-dash count is zero, and the repo
is committed locally. Not pushed; Henri creates the public repo and adds the
remote.

## Phase 1: MVP (the working core)

One request or document goes end to end through the real machinery. All four
gap-closing technologies are present and exercised, minimally but genuinely.

The MVP is **one path that actually runs**:

1. **Live LLM via provider adapter.** The `extract` node calls a real LLM
   through the `LLMProvider` interface. Default provider is Anthropic. The mock
   provider exists alongside it for tests. Output is validated by the config's
   Pydantic v2 schema. This is a real API call, not a stub.
2. **pgvector retrieval.** The `demo_quarry` policy snippets are embedded and
   stored in a pgvector table. The `retrieve` node embeds the request and runs
   a top-k similarity query, returning snippets with their source citations.
   This is real retrieval against a real Postgres, not a hardcoded list.
3. **LangGraph 4-node flow.** The graph wires intake to extract to retrieve to
   decide or escalate, with a conditional edge selecting the decision or
   escalation output path. State is typed.
4. **Docker deploy.** A Dockerfile builds the app and a compose file brings up
   the app plus a pgvector-enabled Postgres so the whole flow runs in
   containers locally. This proves the deploy path even before a hosted URL.

Also in Phase 1:

- Audit log written at every node (input, fields, retrieved context and
  sources, decision, reasoning, confidence).
- Human-in-the-loop escalation: low confidence or a rule trigger routes to an
  escalation outcome instead of a decision.
- A CLI entry point that runs one synthetic sample through the flow and prints
  the decision plus the audit record.
- Smoke and unit tests using the mock provider so the flow is testable without
  spend or network.

Explicitly NOT in Phase 1: a hosted URL, a UI, multiple configs, SaaS
integrations, authentication, or scale or performance work.

## Phase 2: hardening and a second config

- Add one more synthetic config (for example credit or underwriting) to prove
  the core vs config separation with a second domain.
- Better extraction prompts, retries on validation failure, and confidence
  calibration.
- Structured, queryable audit storage (audit rows in Postgres).
- A second LLM provider adapter (for example OpenAI) to prove vendor
  portability.
- CI running the test suite.

## Phase 3: deploy and demo

- Deploy to Fly.io so the demo has a public URL.
- A minimal FastAPI plus HTML UI: paste a synthetic request, see the decision,
  citations, and audit trail.
- One SaaS integration (for example post escalations to a Slack channel).
- A short recorded walkthrough for the portfolio.

Only after Phase 3 may the project be described as deployed or demonstrated.
See [claims-map.md](claims-map.md).

## Phase ordering principle

The four gap-closing technologies are not spread across phases. They all land
in the Phase 1 MVP so the core is honestly "real" end to end as early as
possible. Later phases add breadth (more configs, more providers, a UI, a
hosted URL), not the missing fundamentals.
