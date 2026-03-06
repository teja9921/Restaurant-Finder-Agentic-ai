"""Conditional edge functions for routing."""
from typing import Literal
from src.application.orchestrator.workflow.state import OrchestratorState

def route_intent(
        state: OrchestratorState,
)-> Literal["search", "chat"]:
    """
    Route based on classified intent.

    Returns node name to execute next.
    """
    intent = state.get("intent", "simple")

    if intent == "restaurant_search":
        return "search"
    else:
        # Both 'simple' and 'off_topic' go to chat
        return "chat"