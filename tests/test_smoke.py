"""Smoke test scaffold (Phase 0 placeholder).

Phase 1 will assert the full flow runs end to end with the mock provider and
produces a well-formed result plus a complete audit record. It will also cover
the escalation path (a rule-tripping synthetic sample yields `escalate` with the
expected rule cited) and schema validation (good payload validates, malformed
payload is rejected).

Phase 0 has no logic to test. The placeholder below documents the intended
checks and is skipped so the suite stays green without dependencies installed.
"""

import pytest


@pytest.mark.skip(reason="Phase 0 scaffold: no application logic yet")
def test_end_to_end_with_mock_provider():
    # Phase 1:
    #   run build_graph(demo_quarry, MockProvider(), test_store) on a sample
    #   assert result has decision/escalation, reasoning, confidence, citations
    #   assert audit record covers intake, extract, retrieve, decide
    ...


@pytest.mark.skip(reason="Phase 0 scaffold: no application logic yet")
def test_escalation_path():
    # Phase 1:
    #   feed the new-customer-over-200t sample
    #   assert outcome == "escalate" and "CREDIT-03" in citations
    ...
