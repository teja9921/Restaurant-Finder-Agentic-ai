"""LLM chains - MVP version."""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_aws import ChatBedrockConverse
from langgraph.prebuilt import create_react_agent
from src.application.orchestrator.workflow.tools import ALL_TOOLS
from src.config import settings
from src.domain.prompts import ROUTER_SYSTEM_PROMPT,SEARCH_AGENT_PROMPT,CHAT_AGENT_PROMPT

def get_router_chain():
    """Get router chain for intent classification"""
    model = get_model(temperature=0.0)

    prompt = ChatPromptTemplate([
        ("system", ROUTER_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ])

    return prompt | model

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

def get_chat_agent():
    """Get simple chat agent (no tools)."""
    model = get_model(temperature=0.7)

    prompt = ChatPromptTemplate([
        ("system", CHAT_AGENT_PROMPT),
        MessagesPlaceholder(variable_name="messages")
    ])

    return prompt | model