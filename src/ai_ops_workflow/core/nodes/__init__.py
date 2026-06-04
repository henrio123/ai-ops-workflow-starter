"""LangGraph nodes for the 4-node flow.

intake, extract, retrieve, decide. Each is a pure-ish function over
WorkflowState that calls injected dependencies (LLM provider, vector store,
config) and writes its results plus an audit entry back to state.

Phase 0: placeholder modules only.
"""
