# Config schema

A client or domain is added as a **config**, never as new core code. This
document defines what a config contains and how the core loads it.

## Where configs live

```
src/ai_ops_workflow/configs/
├── __init__.py            # registry: maps config name -> config object
└── <config_name>/
    ├── __init__.py        # builds and exposes the WorkflowConfig
    ├── config.yaml        # declarative settings (thresholds, types, prompts)
    ├── schemas.py         # Pydantic v2 extraction schema for this domain
    ├── policy.py          # decision policy function (pure, typed)
    ├── policies/          # rule and policy source text (seeds the vector store)
    │   └── rules.md
    └── samples/           # synthetic example requests for tests and demo
        └── sample_request.json
```

## The config object

The core consumes a single typed `WorkflowConfig`. Conceptually it has these
fields (final field names are set in Phase 1):

| Field                  | Type                         | Purpose                                                |
| ---------------------- | ---------------------------- | ------------------------------------------------------ |
| `name`                 | `str`                        | Unique config id, used in audit and the registry.      |
| `description`          | `str`                        | Human summary of the domain.                           |
| `document_types`       | `list[str]`                  | Request or document types intake will accept.          |
| `extraction_schema`    | `type[BaseModel]`            | Pydantic v2 model the extractor validates against.     |
| `extraction_prompt`    | `str` (template)             | Prompt template guiding field extraction.              |
| `rules_source`         | `path or list[str]`          | Policy and rule snippets that seed the vector store.   |
| `decision_policy`      | `Callable[..., Decision]`    | Pure function mapping fields plus rules to a decision. |
| `decision_prompt`      | `str` (template, optional)   | Prompt template if the decision step uses the LLM.     |
| `escalation_thresholds`| `EscalationThresholds`       | Confidence floor and rule triggers for human review.   |
| `retrieval`            | `RetrievalSettings`          | top-k, embedding provider/model (via `EmbeddingProvider`), similarity metric. |

The core treats `extraction_schema` and `decision_policy` as opaque callables
and types. It never inspects domain meaning; it only runs them.

## config.yaml (declarative part)

The parts that are plain data live in YAML so a non-engineer can tune them:

```yaml
name: demo_quarry
description: Synthetic quarry order intake and approval demo.
document_types:
  - aggregate_order
  - delivery_request
retrieval:
  top_k: 4
  # The embedding model is resolved by the EmbeddingProvider, a sibling of the
  # chat/completion LLMProvider. It can be a different provider than the one
  # used for extraction; retrieval is not coupled to the chat provider.
  embedding_model: text-embedding-default
  similarity: cosine
escalation:
  min_confidence: 0.70        # below this, escalate to a human
  always_escalate_when:
    - order_volume_tonnes_gt: 500
    - new_customer: true
prompts:
  extraction_template_file: prompts/extraction.txt
  decision_template_file: prompts/decision.txt
```

Values that are code (the Pydantic schema, the decision policy function) live in
`schemas.py` and `policy.py` and are wired together in the config's
`__init__.py`.

## schemas.py (typed part)

Defines the domain's extraction target as a Pydantic v2 model, for example:

```python
# Illustrative only. Real implementation lands in Phase 1.
class AggregateOrderFields(BaseModel):
    customer_name: str
    material: str
    volume_tonnes: float = Field(gt=0)
    delivery_date: date | None = None
    new_customer: bool = False
```

The extractor asks the LLM to fill this shape, then validates. Validation
failure is a signal, low confidence or a retry, not a crash.

## policy.py (decision part)

A pure, typed function. It receives the validated fields and the retrieved
rules and returns a `Decision` (or signals escalation). It contains no LLM call
itself; if the decision needs the model, the node uses `decision_prompt` and
the provider, then the policy function interprets the result. Keeping it pure
makes it unit-testable with the mock provider.

## Registry

`configs/__init__.py` maps a config name to its `WorkflowConfig`. The runtime
selects a config by name (CLI argument, environment variable, or API field).
Adding a domain is: create the folder, build the `WorkflowConfig`, register the
name. No core change.

## Escalation thresholds

Two mechanisms, both config-owned:

1. **Confidence floor** (`min_confidence`): if extraction or decision
   confidence is below it, escalate.
2. **Rule triggers** (`always_escalate_when`): declarative conditions on
   extracted fields that force human review regardless of confidence.

The core enforces these uniformly; the values are per-config.

## What a config must NOT contain

- Real client data. Only synthetic samples. See
  [data-privacy.md](data-privacy.md).
- Secrets or credentials. Those come from environment, never the config.
- Forks of core logic. If a config needs a core change, that is a core feature
  request, not a per-client patch.
