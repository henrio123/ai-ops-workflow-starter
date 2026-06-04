# Data privacy

This repository is public-bound. The rule is simple and absolute: **only
synthetic data ever lives here.** Real client data, real operational records,
and secrets never get committed.

## Synthetic-only rule

- Every sample request, customer name, price, and rule in this repo is
  invented for demonstration. The demo operator "Demo Kruusakarjaar OU" is
  fictional.
- No real customer, order, contract, or document may be added to `configs/`,
  `tests/`, `docs/`, or anywhere else in the repo.
- Synthetic data must be obviously synthetic: placeholder names, round numbers,
  and a note in the file or its directory README that it is fabricated.

## How real client data stays separate

When this starter is used for an actual engagement, the real config and data
live **outside** the public repo:

- Real configs live in a private repository or a private path, built against
  the same `WorkflowConfig` interface. The public repo provides the core and
  the synthetic `demo_quarry` config only.
- Real rule and policy text is loaded at runtime from a private source
  (private repo, mounted volume, or a secrets-managed store), never checked
  into this repo.
- Real requests and documents are processed at runtime and recorded in the
  audit log of the deployed instance, which is private infrastructure, not in
  this repo.
- Environment variables supply all credentials and connection strings. The
  repo ships `.env.example` with placeholder values only.

The separation is enforced by the core vs config boundary: the core is generic
and public; client specifics are a config that can live anywhere that satisfies
the interface.

## What must never be committed

- API keys, tokens, passwords, or connection strings (use `.env`, which is
  gitignored; commit only `.env.example` with placeholders).
- Real customer, supplier, or employee names or contact details.
- Real prices, contracts, volumes, or any commercially sensitive figures.
- Real policy or rule documents owned by a client.
- Production database dumps, audit logs from real runs, or embeddings derived
  from real data.
- Any file a client provided under confidentiality.

## Enforcement

- `.gitignore` excludes `.env`, virtual environments, caches, and a
  `data/private/` path reserved for local real data that must stay out of git.
- A future pre-commit hook (Phase 1 or later) can scan staged files for common
  secret patterns. Until then, the rule is enforced by review discipline.
- Phase 1 should add a simple local secret-scan check or pre-commit hook for
  common secret patterns, `.env` leakage, private data paths, and obvious
  real-person identifiers in demo files.
- If real data is committed by mistake, treat it as a leak: rotate any exposed
  secret, and scrub history before the repo is made public.

## Note on LLM provider data handling

Extraction sends request or document text to an LLM provider. For the public
demo this is synthetic text only. For real engagements, the provider choice and
its data-retention terms are part of the deployment decision, handled in the
private deployment, and are out of scope for this public repo. The
provider-adapter design makes it possible to switch to a local provider or a
provider/deployment mode with stricter retention requirements when an engagement
requires it.
