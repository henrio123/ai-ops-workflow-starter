# Architecture

This document describes the layers, the data flow, the technology choices and
why each was made, how the core stays domain-agnostic, and the provider-adapter
LLM design.

## Layers

The system is built as a pipeline of six responsibilities. The first five are
LangGraph-visible workflow stages; audit cuts across all of them.

1. **Intake** - receive an operational request or document, attach metadata
   (config name, timestamp, request id), and normalise it into the graph
   state. No domain logic; the config says what document types are allowed.
2. **Extract** - call the LLM (through a provider adapter) to pull structured
   fields out of the raw text, then validate them against the config's
   Pydantic v2 schema. Produces typed fields plus an extraction confidence.
3. **Retrieve** - embed the extracted fields or the request text, query the
   pgvector store for the top-k most similar policy and rule snippets, and
   return them with their source citations.
4. **Decide or escalate** - apply the config's decision policy to the
   extracted fields and retrieved rules. If confidence is below the config's
   threshold, or a rule demands human review, route to escalation instead of
   deciding. Otherwise emit a recommended decision.
5. **Output** - assemble the final result: decision, reasoning, confidence,
   cited context, and escalation flag.
6. **Audit** - record every step: raw input, extracted fields, retrieved
   context and sources, decision, reasoning, and confidence. This is a
   cross-cutting concern written at each node, not a single stage.

## Data flow

```
                         +----------------------+
   request / document    |        INTAKE        |
   (synthetic) --------> |  normalise + metadata|
                         +----------+-----------+
                                    |  state
                                    v
                         +----------------------+        +------------------+
                         |        EXTRACT       | <----> |   LLM provider   |
                         | LLM -> Pydantic v2   |        | adapter (default |
                         | typed fields + conf. |        |   Anthropic)     |
                         +----------+-----------+        +------------------+
                                    |  fields, confidence
                                    v
                         +----------------------+        +------------------+
                         |       RETRIEVE       | <----> |  pgvector store  |
                         | embed -> top-k rules |        | policy snippets  |
                         | + source citations   |        | + embeddings     |
                         +----------+-----------+        +------------------+
                                    |  rules, citations
                                    v
                         +----------------------+
                         |   DECIDE / ESCALATE  |
                         | policy + thresholds  |
                         |  confidence gate     |
                         +----------+-----------+
                            |                |
              low conf. /   |                |  pass
              rule says     |                v
              human         |     +----------------------+
                            |     |        OUTPUT        |
                            |     | decision + reasoning |
                            v     | + citations + flag   |
                   +-------------+ +----------+-----------+
                   |  ESCALATE   |            |
                   |  to human   |            |
                   +------+------+            |
                          |                   |
                          v                   v
                   +------------------------------------+
                   |               AUDIT LOG            |
                   | input, fields, context+sources,   |
                   | decision, reasoning, confidence   |
                   +------------------------------------+
```

Both the escalate path and the decide path produce an output object and an
audit record. Escalation is a first-class outcome, not an error.

## LangGraph node mapping

The MVP graph has exactly four nodes plus a conditional edge:

| Node      | Reads from state         | Writes to state               |
| --------- | ------------------------ | ----------------------------- |
| `intake`  | raw input, config name   | normalised request, metadata  |
| `extract` | normalised request       | extracted fields, confidence  |
| `retrieve`| extracted fields / text  | retrieved rules, citations    |
| `decide`  | fields, rules, thresholds| decision OR escalation flag   |

A conditional edge after `decide` selects the output assembly path
(decision vs escalation). Output assembly and audit writing are utilities the
nodes call, kept thin so the graph stays the 4-node flow that was locked.

## Technology choices and why

- **Python with Pydantic v2.** The extraction boundary is where an LLM's free
  text becomes typed data. Pydantic v2 gives validation, coercion, and clear
  errors at exactly that boundary, and its schema can be emitted to guide the
  LLM. Typed throughout so configs are checkable.
- **LangGraph for the flow.** The decision process is a small state machine
  with a branch (decide vs escalate). LangGraph models this explicitly as
  nodes and conditional edges, keeps state typed, and makes the
  human-in-the-loop branch a visible part of the graph rather than a buried
  `if`. Four nodes keep it legible.
- **pgvector on Postgres for retrieval.** Policies and rules are the ground
  truth a decision must cite. pgvector keeps embeddings next to relational
  data (snippet text, source, version) in one store, so retrieval returns the
  snippet and its citation together, and the audit log can record exactly
  which rows were used. One database instead of a separate vector service
  keeps the deploy small.
- **Provider-adapter LLM layer.** See below. Decouples the workflow from any
  single vendor.
- **Dockerized local run, Fly.io later.** Docker is the planned reproducible
  local container run: one image with the app plus a pgvector-enabled Postgres,
  so the whole flow runs in containers on a developer machine. Fly.io is the
  planned Phase 3 hosted target, used only after the local MVP works to put the
  demo on a URL. Phase 1 is local containers only; nothing is hosted yet.

## How the core stays domain-agnostic

The core (`src/ai_ops_workflow/core/`, `llm/`, `retrieval/`) contains no
mention of quarries, orders, claims, or any domain. It only knows:

- the **shape** of the graph state (generic fields like `raw_input`,
  `extracted`, `retrieved`, `decision`);
- how to call an **LLM provider** through an interface;
- how to run **retrieval** against a generic snippets table;
- how to read a **config object** that supplies the domain specifics.

Everything domain-specific is injected by the config:

- the Pydantic schema the extractor validates against;
- the document and request types accepted at intake;
- the rules and policy source that seeds the vector store;
- the decision policy function and the escalation thresholds;
- the prompt templates used for extraction and decision.

For a domain that fits the existing engine contract, adding it means adding a
folder under `configs/` and registering it. If a new domain needs a new generic
capability, that belongs in the core as a deliberate feature, not as a
per-client patch. This is the same separation discipline the project applies
everywhere: generic engine, declarative client.

## Provider-adapter LLM design

The LLM layer exposes two small sibling protocols and several implementations.
`LLMProvider` handles completion and extraction (the chat-style calls). A
separate `EmbeddingProvider` handles embeddings for retrieval. They are
deliberately distinct interfaces, not one protocol with an `embed()` method
bolted on.

```
        core / extract node            core / retrieve node
                |                                |
                v                                v
      +-------------------+            +----------------------+
      |  LLMProvider      |            |  EmbeddingProvider   |
      |  - complete()     |            |  - embed()           |
      |  - extract()      |            +----------------------+
      +-------------------+                /            \
          /     |      \                  v              v
         v      v       v          (embedding model    Mock / local
   Anthropic OpenAI  Mock/Local     adapter; may be    embedder
   provider  provider provider      a different vendor (tests, offline)
   (Phase 1  (later)  (tests,        than the chat
    default)         offline)        provider)
```

Principles:

- The core's extract and decide nodes call only the `LLMProvider` interface,
  and the retrieve node calls only the `EmbeddingProvider` interface, never a
  vendor SDK directly. Swapping either is a config or environment change, not a
  code change in the workflow.
- The **default planned extraction provider for Phase 1 is Anthropic.** OpenAI,
  a local model, and a deterministic mock are designed in from the start so
  they can be added later without touching node logic.
- **Extraction and embeddings may use different providers.** The embedding
  provider is chosen independently of the chat or completion provider, because
  the best or cheapest embedding model may come from a different vendor, and
  retrieval must not be coupled to whichever provider does extraction. The repo
  does not assume Anthropic supplies embeddings.
- Keeping `EmbeddingProvider` separate means the retrieval layer stays
  vendor-neutral on its own terms: a change of chat provider does not force a
  change of embedding model, and vice versa.
- The **mock provider** is part of the design, not an afterthought: a mock
  `LLMProvider` and a mock `EmbeddingProvider` let the graph, retrieval, and
  audit be exercised in tests without network calls or spend.

## Audit as a cross-cutting concern

Every node appends to a structured audit record keyed by request id. The record
captures input, extracted fields, retrieved context with sources, the decision
or escalation, the reasoning, and the confidence. Because retrieval returns
citations, the audit answers "which policy text drove this decision", which is
the property that makes the system defensible for operational use.
