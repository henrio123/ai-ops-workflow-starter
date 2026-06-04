# Demo use case: synthetic quarry order workflow

This is the one example config shipped on the general core. It is fully
synthetic. There is no real client, no real quarry, and no real order behind
it. The fictional operator is "Demo Kruusakarjaar OU".

> All names, prices, customers, and rules below are invented for
> demonstration. See [data-privacy.md](data-privacy.md).

## The scenario

A small aggregates quarry receives order requests by email and web form. An
operations person reads each one, checks it against the price list and the
business rules (minimum volumes, delivery radius, credit terms for new
customers, permit limits), and either confirms the order, requests changes, or
flags it for a manager.

The demo automates the first pass: extract the order fields, retrieve the
relevant rules, recommend confirm or revise, and escalate the cases a human
should still see.

## Config: `demo_quarry`

| Aspect            | Value (synthetic)                                            |
| ----------------- | ----------------------------------------------------------- |
| Config name       | `demo_quarry`                                                |
| Document types    | `aggregate_order`, `delivery_request`                        |
| Decisions         | `confirm`, `revise`, `escalate`                              |
| Escalation floor  | confidence `< 0.70`                                          |
| Hard escalations  | volume over 500 t, or a new customer over a credit limit     |

## Extraction schema (illustrative)

The config's `schemas.py` targets a Pydantic v2 model along these lines:

```
AggregateOrderFields
  customer_name: str
  material: str                  # e.g. "0-16 crushed gravel"
  volume_tonnes: float (> 0)
  delivery_distance_km: float (>= 0)
  delivery_date: date | None
  new_customer: bool
```

## Rules and policy source (synthetic snippets)

These seed the pgvector store. Each is stored with a source id so the decision
can cite it. Examples of the kind of snippet, all invented:

- `PRICE-01` Minimum billable load is 5 tonnes. Orders below 5 t are revised
  to the minimum or escalated.
- `DELIV-02` Standard delivery radius is 40 km. Beyond 40 km a surcharge
  applies and the order is escalated for a manual quote.
- `CREDIT-03` New customers ordering above 200 t must be on prepayment.
  Otherwise escalate for a credit check.
- `PERMIT-04` Daily extraction permit cap is 800 t. Orders that would push the
  day over the cap are escalated.
- `MAT-05` Materials list and grades the quarry actually stocks. Requests for
  an unstocked grade are revised with the nearest available grade.

The full synthetic snippet text lives in
`src/ai_ops_workflow/configs/demo_quarry/policies/rules.md`.

## Walkthrough (what the flow will do in Phase 1)

1. **Intake**: a synthetic `aggregate_order` request arrives (see
   `configs/demo_quarry/samples/sample_request.json`).
2. **Extract**: the LLM fills `AggregateOrderFields`; Pydantic validates.
   Suppose volume 250 t, new customer true, distance 22 km.
3. **Retrieve**: top-k snippets come back including `CREDIT-03`.
4. **Decide or escalate**: new customer over 200 t triggers `CREDIT-03`, so the
   flow escalates for a credit check rather than auto-confirming. The output
   cites `CREDIT-03` as the reason.
5. **Audit**: the whole chain is recorded, including which snippet drove the
   escalation.

A second sample (small in-radius repeat-customer order) would pass straight to
`confirm` with the cited price and delivery rules.

## Why a quarry demo

It is concrete, unglamorous operations work with clear rules and clear
escalation cases, which shows the core's value (consistent triage with an audit
trail) without needing a regulated or sensitive domain. It is also easy to keep
entirely synthetic.

## What this demo is not

This is not quarry management software. The quarry workflow is only a synthetic
example config used to demonstrate the reusable core: extraction, retrieval,
decision routing, escalation, and audit. The business value is the pattern, not
the quarry domain.

## Planned Phase 1 samples

- `sample_escalate_new_customer.json`: new customer, 250 t, in radius. Expected
  outcome: `escalate`, citing `CREDIT-03`.
- `sample_confirm_repeat_customer.json`: repeat customer, 40 t, in radius,
  stocked material. Expected outcome: `confirm`, citing price and delivery
  snippets.

## Other configs plug into the same core

The same core serves other domains by adding a config:

- **Credit or underwriting**: extract applicant and loan fields, retrieve
  lending policy, recommend approve or refer, escalate thin-file or
  over-limit cases.
- **Insurance or claims**: extract claim fields, retrieve coverage and
  exclusion rules, recommend pay, request docs, or refer to an adjuster.

For a domain that fits the existing engine contract, adding it means adding a
folder under `configs/` and registering it: a new schema, a new rules source,
and a new decision policy, while the intake, extract, retrieve, decide, output,
and audit machinery is shared. If a new domain needs a new generic capability,
that belongs in the core as a deliberate feature, not as a per-client patch.
