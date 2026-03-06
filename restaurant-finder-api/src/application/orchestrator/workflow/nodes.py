"""Graph nodes - MVP version."""
from typing import Dict, Any
from langchain_core.messages import AIMessage, HumanMessage
from src.application.orchestrator.workflow.state import OrchestratorState
from src.application.orchestrator.workflow.chains import (
    get_router_chain,
    get_search_agent,
    get_chat_agent
)
from src.infrastructure.memory import memory_manager

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
    
    preferences = memory_manager.get_user_preferences(session_id)
    if preferences:
        pref_text = "User preferences: " + ", ".join(
        f"{k}={v}" for k,v in preferences.items()
        )
        messages = list(messages) + [HumanMessage(content=pref_text)]
    
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

async def memory_hook_node(state: OrchestratorState) -> Dict[str, Any]:
    """
    Memory post-hook - stores conversation to long-term memory.
    
    Runs after agent responds. Decides whether to store interaction.
    """
    messages = state["messages"]
    session_id = state.get("session_id", "default")

    #Need atleast user_message + assistant response
    if len(messages)<2:
        return {}
    
    user_msg = messages[-2]
    assistant_msg = messages[-1]

    #Store conversation turn
    memory_manager.store_conversation_turn(
        session_id, 
        user_message = user_msg.content if hasattr(user_msg, 'content') else str(user_msg),
        assistant_message = assistant_msg.content if hasattr(assistant_msg, 'content') else str(assistant_msg),
    )

    #Extract and store preferences (simple pattern matching for sprint4)
    user_content = user_msg.content if hasattr(user_msg, 'content') else str(user_msg)
    user_lower = user_content.lower()

    #Detect dietary preferences
    if "vegan" in user_lower or "i'm vegan" in user_lower:
        memory_manager.store_user_preference(
            session_id,
            preference_type = 'dietary',
            value = 'vegan'
        )

    elif "vegetarian" in user_lower:
        memory_manager.store_user_preference(
            session_id,
            preference_type = 'dietary',
            value = 'vegetarian'
        )

    
    #Detect price preferences
    if "cheap" in user_lower or "budget" in user_lower:
        memory_manager.store_user_preference(
            session_id,
            preference_type = 'price',
            value = 'budget'
        )
    
    elif "expensive" in user_lower or "finedining" in user_lower:
        memory_manager.store_user_preference(
            session_id,
            preference_type = 'price',
            value = 'expensive'
        )

    return {}