"""Main entry point with router testing."""
import asyncio
from langchain_core.messages import HumanMessage
from src.application.orchestrator.workflow.graph import graph

async def run_agent(user_input: str, session_id: str = "test"):
    """Run the agent."""
    print(f"\n{'='*60}")
    print(f"User: {user_input}")
    print(f"{'='*60}\n")
    
    result = await graph.ainvoke(
        input={
            "messages": [HumanMessage(content=user_input)],
            "session_id": session_id,
            "customer_name": "Test User",
            "intent": "",
            "tool_call_count": 0,
            "made_tool_calls": False,
        }
    )
    
    # Print response
    final_message = result["messages"][-1]
    print(f"Agent: {final_message.content}\n")
    print(f"Intent: {result.get('intent', 'N/A')}")
    print(f"Tool calls: {result.get('tool_call_count', 0)}\n")


if __name__ == "__main__":
    # Test different intents
    asyncio.run(run_agent("Hello!"))  # Should route to chat
    asyncio.run(run_agent("Find Italian restaurants in Mumbai"))  # Should route to search
    asyncio.run(run_agent("Thanks!"))  # Should route to chat