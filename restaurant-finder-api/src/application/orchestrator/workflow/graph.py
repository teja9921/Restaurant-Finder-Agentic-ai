"""LangGraph workflow - MVP version."""
from langgraph.graph import StateGraph, END
from src.application.orchestrator.workflow.state import OrchestratorState
from src.application.orchestrator.workflow.nodes import search_agent_node


def create_workflow() -> StateGraph:
    """Create simple linear workflow."""
    workflow = StateGraph(OrchestratorState)
    
    # Single node
    workflow.add_node("search_agent", search_agent_node)
    
    # Linear flow: START -> search_agent -> END
    workflow.set_entry_point("search_agent")
    workflow.add_edge("search_agent", END)
    
    return workflow


# Compile graph
graph = create_workflow().compile()
