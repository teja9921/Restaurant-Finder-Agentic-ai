"""Workflow state definition - MVP version."""
from typing import TypedDict, List, Annotated, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

IntentType = Literal["restaurant-search", "simple", "off_topic"]
class OrchestratorState(TypedDict):
    """State for the orchestrator with router pattern."""
    
    messages: Annotated[List[BaseMessage], add_messages]
    session_id: str
    customer_name: str
    intent: IntentType
    tool_call_count: int
    made_tool_calls: bool