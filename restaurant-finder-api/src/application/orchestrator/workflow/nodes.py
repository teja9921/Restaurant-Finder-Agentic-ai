"""Graph nodes - MVP version."""
from typing import Dict, Any
from langchain_core.messages import AIMessage
from src.application.orchestrator.workflow.state import OrchestratorState
from src.application.orchestrator.workflow.chains import (
    get_router_chain,
    get_search_agent,
    get_chat_agent
)

async def router_node(state: OrchestratorState) -> Dict[str, Any]:
    """Router node - classifies user intent."""
    messages = state["messages"]

    #invoke router chain
    chain = get_router_chain()
    resposne = await chain.ainvoke({"messages": messages})
    intent = resposne.content.strip().upper()

    #Normalize to valid intent
    if "SEARCH" in intent:
        intent = "restaurant_search"
    elif "SIMPLE" in intent:
        intent = "simple"
    else:
        intent = "off_topic"

    return {
        "intent": intent,
        "tool_call_count": 0,
        "made_tool_calls": False
    }


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
    
    # Check if agent made tool calls
    made_tools = False
    tool_count = 0
    
    # Count tool messages in the response
    for msg in response.get("messages", []):
        if hasattr(msg, 'type') and msg.type == 'tool':
            made_tools = True
            tool_count += 1
    
    # Return updated messages and tool tracking
    return {
        "messages": response["messages"],
        "made_tool_calls": made_tools,
        "tool_call_count": state.get("tool_call_count", 0) + tool_count,
    }

async def chat_agent_node(state: OrchestratorState) -> Dict[str, Any]:
    """Chat agent node - simple conversation."""
    messages = state["messages"]

    chain = get_chat_agent()
    response = await chain.ainvoke({"messages": messages})

    return {
        "messages": [AIMessage(content = response.content)]
    }