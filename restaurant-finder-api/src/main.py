"""Main entry point - MVP version."""
import asyncio
from langchain_core.messages import HumanMessage
from src.application.orchestrator.workflow.graph import graph

async def run_agent(user_input: str, session_id: str = "test"):
    """Run the agent."""
    print(f"\nUser: {user_input}\n")
    
    result = await graph.ainvoke(
        input={
            "messages": [HumanMessage(content=user_input)],
            "session_id": session_id,
        }
    )
    
    # Print response
    final_message = result["messages"][-1]
    print(f"Agent: {final_message.content}\n")
    print("=" * 50)


if __name__ == "__main__":
    # Test scenarios
    asyncio.run(run_agent("Find Italian restaurants in San Francisco"))
    asyncio.run(run_agent("What about Chinese food?"))