"""AgentCore API wrapper for deployment."""
try:
    from bedrock_agentcore.runtime import BedrockAgentCoreApp
    AGENTCORE_AVAILABLE = True
except ImportError:
    AGENTCORE_AVAILABLE = False
    print("[API] bedrock_agentcore not available, usig local mode only")

from langchain_core.messages import HumanMessage
from src.application.orchestrator.workflow.graph import graph
from src.application.orchestrator.streaming import stream_response_content
from src.infrastructure.guardrails import apply_input_guardrails, apply_output_guardrails
from src.config import settings

if AGENTCORE_AVAILABLE:
    # AgentCore App for production deployment
    app = BedrockAgentCoreApp()


    @app.on_event("startup")
    async def startup():
        """Intializes services on application startup"""
        print(f"✓ Agent runtime started: {settings.OTEL_SERVICE_NAME}")
        print(f"✓ Region: {settings.AWS_REGION}")
        print(f"✓ Guardrails: {'Enabled' if settings.GUARDRAIL_ENABLED else 'Disabled'}")

    @app.entrypoint
    async def invoke_agent(payload: dict):
        """
        Main entrypoint for AgentCore Runtime.

        Recieves HTTP invocations and returns agent responses.

        Args:
            payload: Dict with keys:
                - prompt: User message
                - session_id: conversation identifier
                - customer_name: User's name (optional)

        Returns:
            Dict with response content
        """

        # Extract inputs
        user_input = payload.get("prompt", "")
        session_id = payload.get("session_id", "default")
        customer_name = payload.get("customer_name", "Guest")

        #Apply input guardrails
        if settings.GUARDRAIL_ENABLED:
            validated_input = apply_input_guardrails(user_input)
            if not validated_input:
                return {
                    "response": "I'm sorry, I can't procees that request.",
                    "blocked": True
                }
            user_input = validated_input

        # Create message
        messages = [HumanMessage(content=user_input)]

        # Configure session
        config = {
            "configurable": {"thread_id": session_id}
            }
        
        # Invoke graph
        result = await graph.ainvoke(
            input = {
                "messages": messages,
                "session_id": session_id,
                "customer_name": customer_name,
                "intent": "",
                "tool_call_count": 0,
                "made_tool_calls": False,
            },
            config = config
        )

        # Extract final response
        final_message = result["messages"][-1]
        response_content = getattr(final_message, 'content', str(final_message))
        
        # Apply output guardrails
        if settings.GUARDRAIL_ENABLED:
            validated_output = apply_output_guardrails(response_content)
            if not validated_output:
                return {
                    "response": "I apologize, but I cannot provide that information.",
                    "blocked": True,
                }
            response_content = validated_output
        
        return {
            "response": response_content,
            "session_id": session_id,
        }


    if hasattr(app, "streaming_entrypoint"):
        @app.streaming_entrypoint
        async def stream_agent(payload: dict):
            """
            Streaming entrypoint for real-time responses.
            
            Used when client wants to receive response as it's generated.
            
            Args:
                payload: Same as invoke_agent
                
            Yields:
                Content chunks
            """
            user_input = payload.get("prompt", "")
            session_id = payload.get("session_id", "default")
            customer_name = payload.get("customer_name", "Guest")
            
            # Apply input guardrails
            if settings.GUARDRAIL_ENABLED:
                validated_input = apply_input_guardrails(user_input)
                if not validated_input:
                    yield "I'm sorry, I can't process that request."
                    return
                user_input = validated_input
            
            messages = [HumanMessage(content=user_input)]
            
            async for chunk in stream_response_content(
                graph=graph,
                messages=messages,
                session_id=session_id,
                customer_name=customer_name,
            ):
                yield chunk
    else:
        print("[API] streaming_entrypoint not available in this bedrock_agentcore version; streaming disabled")
    
    
    if __name__ == "__main__":
        # For local development with agentcore dev
        app.run(host="0.0.0.0", port=8080)

else:
    # Fallback for local development without AgentCore
    print("[API] Running in local mode without AgentCore")


