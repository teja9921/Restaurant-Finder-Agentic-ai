"""Workflow state definition - MVP version."""
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class OrchestratorState(TypedDict):
    """State for the orchestrator."""
    
    messages: Annotated[List[BaseMessage], add_messages]
    session_id: str