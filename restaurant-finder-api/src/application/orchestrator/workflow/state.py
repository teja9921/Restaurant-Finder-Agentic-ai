from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import add_messages

class OrchestratorState(TypedDict):
    """
    State passed through the workflow graph.

    This state is modified by each node and contains all context 
    needed for routing decisions and agent execution.
    """

    #Messages
    messages: Annotated[List[Dict[str, Any]], add_messages]

    #User context 
    user_query: str
