"""Graph nodes - MVP version."""
from typing import Dict, Any
from src.application.orchestrator.workflow.state import OrchestratorState
from src.application.orchestrator.workflow.chains import get_search_agent

async def search_agent_node(state: OrchestratorState) -> Dict[str, Any]:
    """Search agent node with tool support."""
    messages = state["messages"]
    session_id = state.get("session_id", "default")
    
    # Get ReAct agent
    agent = get_search_agent()
    
    # Invoke with config for session
    config = {"configurable": {"thread_id": session_id}}
    response = await agent.ainvoke(
        {"messages": messages},
        config=config,
    )
    
    # Return updated messages
    return {
        "messages": response["messages"],
    }