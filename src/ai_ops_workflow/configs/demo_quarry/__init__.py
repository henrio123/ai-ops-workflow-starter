"""demo_quarry config (Phase 0 placeholder).

Synthetic example config for a fictional aggregates quarry, "Demo Kruusakarjaar
OU". All data is invented. See docs/demo-use-case.md and docs/data-privacy.md.

This module wires the declarative settings (config.yaml), the extraction schema
(schemas.py), the decision policy (policy.py), and the rules source
(policies/rules.md) into a single WorkflowConfig.

Planned shape (Phase 1):

    def build_config() -> WorkflowConfig:
        # load config.yaml, attach AggregateOrderFields and decide_demo_quarry
        ...

No logic in Phase 0.
"""
