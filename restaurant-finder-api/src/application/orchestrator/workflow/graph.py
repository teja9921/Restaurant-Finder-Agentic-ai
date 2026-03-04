from dotenv import load_dotenv

load_dotenv()
from langgraph.graph import StateGraph, END
from src.application.orchestrator.workflow.state import OrchestratorState
from src.application.orchestrator.workflow.nodes import chat_node


def create_orchestrator_graph():
    """
    Create and compile the orchestrator workflow graph.
    
    Graph Structure:
    START -> chat_node -> END

    Returns:
        Compiled StateGraph ready for invocation
    """

    # Create graph with state schema
    graph = StateGraph(OrchestratorState)

    # Add nodes
    graph.add_node("chat_node", chat_node)

    #set entry point
    graph.set_entry_point("chat_node")

    # Add edges
    graph.add_edge("chat_node", END)

    compiled_graph = graph.compile()

    return compiled_graph

orchestrator_graph = create_orchestrator_graph()

if __name__ == "__main__":
    # Test input
    user_query = "Find me a good South Indian restaurant in Nalgonda"
    
    # Run the chain
    # Note: chat_history is optional=True, so we can pass an empty list
    try:
        # Key must match 'user_query' in OrchestratorState
        final_state = orchestrator_graph.invoke({
            "user_query": user_query, 
            "messages": []
        })
        
        # In LangGraph, the result is in the final message of the list
        last_message = final_state["messages"][-1]
        
        # If your chat_node returns the structured object:
        res = last_message 
        
        print("--- Agent Response ---")
        print(f"Restaurant: {res.name}")
        print(f"Cuisine: {res.cuisine_type}")
        print(f"Address: {res.address}")
        
    except Exception as e:
        print(f"An error occurred: {e}")