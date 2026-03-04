from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.domain.prompts import CHAT_AGENT_PROMPT
from src.domain.models import chat_llm

def create_chat_agent_chain():
    """Create conversational agent"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAT_AGENT_PROMPT),
        MessagesPlaceholder(variable_name="chat_history",
        optional= True),
        ("human", "{query}"),
    ])

    return prompt | chat_llm

chat_agent = create_chat_agent_chain()



