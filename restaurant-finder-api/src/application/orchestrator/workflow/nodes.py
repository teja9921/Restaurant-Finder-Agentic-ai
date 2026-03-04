"""Graph nodes for the orchestrator workflow."""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from src.application.orchestrator.workflow.state import OrchestratorState
from src.application.orchestrator.workflow.chains import chat_agent

def chat_node(state: OrchestratorState) -> Dict[str, Any]:

    messages = state["messages"]

    #Invoke chat agent 
    structured_result = chat_agent.invoke({"query":state["user_query"], "chat_history": messages})

    message = AIMessage(
        content=f"Found restaurant: {structured_result.name}",
        additional_kwargs={"structured_output": structured_result.dict()}
    )
    return {
        "messages": [message]
    }

