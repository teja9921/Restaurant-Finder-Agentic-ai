"""LLM chains - MVP version."""
from langchain_aws import ChatBedrockConverse
from langgraph.prebuilt import create_react_agent

from src.application.orchestrator.workflow.tools import ALL_TOOLS
from src.config import settings
from src.domain.prompts import SEARCH_AGENT_PROMPT


def get_model(temperature: float = 0.7) -> ChatBedrockConverse:
    """Get Bedrock model."""
    return ChatBedrockConverse(
        model=settings.BEDROCK_MODEL_ID,
        temperature=temperature,
        region_name=settings.AWS_REGION,
        credentials_profile_name=settings.AWS_PROFILE,
    )


def get_search_agent():
    """Get ReAct search agent with tools."""
    model = get_model(temperature=0.7)

    agent = create_react_agent(
        model=model,
        tools=ALL_TOOLS,
        prompt=SEARCH_AGENT_PROMPT,
    )

    return agent
