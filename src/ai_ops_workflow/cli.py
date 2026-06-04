"""CLI entry point (Phase 0 placeholder).

In Phase 1 this runs one synthetic sample through the full graph and prints the
decision plus the audit record. It selects a config by name and a provider by
name (mock for offline runs, Anthropic by default for a live run).

Planned usage (Phase 1):

    python -m ai_ops_workflow.cli --config demo_quarry \\
        --provider mock --input <path-to-synthetic-sample.json>

No argument parsing and no execution in Phase 0.
"""
