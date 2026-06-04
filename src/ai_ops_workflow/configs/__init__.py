"""Config registry.

Maps a config name to its WorkflowConfig. The runtime selects a config by name
(CLI argument, environment variable, or API field). Adding a domain is: create
a folder here, build its WorkflowConfig, and register the name below. No core
change is needed.

Planned registry (Phase 1):

    REGISTRY: dict[str, Callable[[], WorkflowConfig]] = {
        "demo_quarry": demo_quarry.build_config,
        # "demo_credit": demo_credit.build_config,   # Phase 2 example
    }

Phase 0: only the synthetic demo_quarry config exists, as scaffold.
"""
