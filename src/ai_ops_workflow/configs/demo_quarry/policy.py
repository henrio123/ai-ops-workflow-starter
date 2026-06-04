"""demo_quarry decision policy (Phase 0 placeholder).

A pure, typed function mapping validated fields plus retrieved rules to a
decision, or signalling escalation. It contains no LLM call itself; if the
decision needs the model, the decide node uses the decision prompt and the
provider, then this function interprets the result. Keeping it pure makes it
unit-testable with the mock provider.

Planned shape (illustrative, implemented in Phase 1), all synthetic rules:

    def decide_demo_quarry(fields: AggregateOrderFields,
                           rules: list[RetrievedSnippet],
                           thresholds: EscalationThresholds) -> Decision:
        # CREDIT-03: new customer over 200 t -> escalate for credit check
        # DELIV-02: distance over 40 km -> escalate for manual quote
        # PRICE-01: volume under 5 t -> revise to minimum
        # otherwise -> confirm, citing the matched rules
        ...

No logic in Phase 0.
"""
