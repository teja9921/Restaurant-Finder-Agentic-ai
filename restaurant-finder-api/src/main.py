"""Main entry point with memory testing."""
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

async def test_memory():
    """Test memory persistence across messages."""
    session_id = "memory-test-session"
    
    print("\n" + "="*60)
    print("MEMORY TEST - Session 1")
    print("="*60)
    
    # First interaction - set preference
    await run_agent("I'm vegan", session_id)
    
    # Second interaction - should remember
    await run_agent("Find restaurants in Mumbai", session_id)
    
    print("\n" + "="*60)
    print("MEMORY TEST - New Session (should not remember)")
    print("="*60)
    
    # New session - should not have preferences
    await run_agent("Find restaurants in Delhi", "new-session")

if __name__ == "__main__":

    #Test memory
    asyncio.run(test_memory())