"""Chainlit UI for Restaurant Finder Agent."""
import os
import json
import uuid
import httpx
from typing import Optional
from chainlit.input_widget import TextInput
import chainlit as cl
from dotenv import load_dotenv

load_dotenv()

# Configuration
CONNECTION_MODE = os.getenv("AGENT_CONNECTION_MODE", "local")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

#AWS Mode
AGENT_RUNTIME_ARN = os.getenv("AGENT_RUNTIME_ARN", "")

# Local Mode
LOCAL_API_URL = os.getenv(
    "AGENTCORE_API_URL",
    "http://localhost:8080/invocations"
)

def get_aws_client():
    """Get AgentCore Runtime client for AWS mode."""
    try:
        import boto3
        return boto3.client('bedrock-agentcore-runtime', region_name=AWS_REGION)
    except ImportError:
        print("[UI] boto3 not available for AWS mode")
        return None
    
    
async def invoke_local_agent(payload: dict) -> str:
    """Invoke agent running locally."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try: 
            response = await client.post(
                LOCAL_API_URL,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No response")
        except httpx.ConnectError:
            return "❌ Cannot connect to local agent. Make sure it's running with: `python -m src.api`"
        except Exception as e:
            return f"❌ Error: {str(e)}"
        

def invoke_aws_agent(payload: dict, session_id: str)-> str:
    """Invoke agent deployed on AWS AgentCore."""
    client = get_aws_client()

    if not client:
        return "❌ boto3 not installed for AWS mode"
    
    if not AGENT_RUNTIME_ARN:
        return "❌ AGENT_RUNTIME_ARN not confiured in .env"
    
    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            qualifier="DEFAULT",
            runtimeSessionId=session_id,
            payload=json.dumps(payload),
        )

        # Parse response
        result = json.loads(response['payload'].read())
        return result.get("response", "No response")
    except Exception as e:
        return f"❌ AWS Error: {str(e)}"
    

@cl.on_chat_start
async def on_chart_start():
    """Intialize chat session."""
    # Create settings panel
    settings = await cl.ChatSettings(
        [
            TextInput(
                id="customer_name",
                label="Your Name",
                placeholder="Enter your name",
                initial="Guest"
            ),
        ]
    ).send()

    # Store user settings
    customer_name = settings.get("customer_name", "Guest")
    cl.user_session.set("customer_name", customer_name)

    # Generate unique conversation ID
    conversation_id = str(uuid.uuid4())
    cl.user_session.set("conversation_id", conversation_id)

    # Send welcome message
    mode_text = "🌐 AWS" if CONNECTION_MODE == "aws" else "💻 Local"

    await cl.Message(
        f"👋 Hi {customer_name}! I'm your restaurant finder assistant ({mode_text} mode).\n\n"
                f"Ask me to find restaurants by cuisine, location, price, or dietary needs!\n\n"
                f"💡 Try: \"Find vegan restaurants in Mumbai\" or \"I prefer budget-friendly places\""
    ).send()
    

@cl.on_settings_update
async def on_settings_update(settings):
    """Handle settings updates."""
    customer_name = settings.get("customer_name", "Guest")
    cl.user_session.set("customer_name", customer_name)
    
    await cl.Message(
        content=f"✓ Updated your name to {customer_name}"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Process user messages."""
    # Retrieve session data
    conversation_id = cl.user_session.get("conversation_id")
    customer_name = cl.user_session.get("customer_name", "Guest")

    # Prepare payload
    payload = {
        "prompt": message.content,
        "session_id": conversation_id,
        "customer_name": customer_name
    }

    # Show loading indicator
    loading_msg = cl.Message(content="🤔 Thinking...")
    await loading_msg.send()

    try:
        # Invoke agent based on mode
        if CONNECTION_MODE == "aws":
            response = invoke_aws_agent(payload, conversation_id)
        else:
            response = await invoke_local_agent(payload)

        # Update message with response
        loading_msg.content = response
        await loading_msg.update()

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        loading_msg.content = error_msg
        await loading_msg.update()


@cl.on_chat_end
async def on_chat_end():
    """Handle chat session end."""
    await cl.Message(
        content="Thanks for using Restaurant Finder! 👋"
    ).send()


if __name__ == "__main__":
    # Run: chainlit run app.py
    pass
