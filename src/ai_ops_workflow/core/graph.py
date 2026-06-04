"""LangGraph 4-node flow assembly (Phase 0 placeholder).

Wires the minimal locked flow:

    intake -> extract -> retrieve -> decide
                                       |
                              conditional edge
                              /              \\
                        (escalate)         (decide)
                             \\              /
                               output + audit

Planned builder (illustrative, implemented in Phase 1):

    def build_graph(config: WorkflowConfig, provider: LLMProvider,
                    store: VectorStore) -> CompiledGraph:
        # StateGraph(WorkflowState)
        # add nodes: intake, extract, retrieve, decide
        # add edges intake->extract->retrieve->decide
        # add conditional edge after decide selecting escalation vs decision
        # output assembly and audit are thin utilities the nodes call
        ...

The graph stays exactly four nodes. Output assembly and audit writing are
helpers, not extra nodes, so the locked flow is preserved.

No logic in Phase 0.
"""
