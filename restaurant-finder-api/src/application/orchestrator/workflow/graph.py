"""LangGraph workflow - MVP version."""
from langgraph.graph import StateGraph, END
from src.application.orchestrator.workflow.state import OrchestratorState
from src.application.orchestrator.workflow.nodes import (
    router_node,
    search_agent_node,
    chat_agent_node,
    memory_hook_node
    )
from src.application.orchestrator.workflow.edges import route_intent


def create_workflow() -> StateGraph:
    """Workflow with router pattern."""
    workflow = StateGraph(OrchestratorState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("search_agent", search_agent_node)
    workflow.add_node("chat_agent", chat_agent_node)
    workflow.add_node("memory_hook", memory_hook_node)

    # Entry point is router
    workflow.set_entry_point("router")
    
    # Conditional routing from router
    workflow.add_conditional_edges(
        "router",
        route_intent,
        {
            "search": "search_agent",
            "chat": "chat_agent"
        }
    )

    # Both agents go to memory hook first, then END
    workflow.add_edge("search_agent", "memory_hook")
    workflow.add_edge("chat_agent", "memory_hook")
    workflow.add_edge("memory_hook", END)
    
    return workflow


# Compile graph
graph = create_workflow().compile()
