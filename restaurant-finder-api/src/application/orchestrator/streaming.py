"""Streaming response handlers for real-time agent output."""
from typing import AsyncIterator, Dict, Any
import json

async def stream_graph_updates(
        graph,
        input_data: Dict[str, Any],
        config: Dict[str, Any]
) -> AsyncIterator[str]:
    """
    Strea m graph execution update as server-sent events.

    Yields JSON strings formatted for SSE consumption.

    Args:
        graph: Compiled LangGraph workflow
        input_data: Input state dictionary
        config: Configuration dict with thread_id

    Yields:
        SSE-formatted event strings
    """
    async for event in graph.astream(input_data, config):
        # Each event is {node_name: node_output}
        for node_name, node_output in event.items():

            #Extract messages from output
            messages = node_output.get("messages", [])

            if messages:
                last_message = messages[-1]

                # Stream content chunks
                if hasattr(last_message, 'content') and last_message.content:
                    yield format_sse_event({
                        "type": "content",
                        "node": node_name,
                        "content": last_message.content
                    })

                #Stream tool calls
                if hasattr(last_message, 'tool_calls'):
                    for tool_call in getattr(last_message, 'tool_calls', []):
                        yield format_sse_event({
                            "type": "tool_call",
                            "tool": tool_call.get("name", "unknown"),
                            "args": toll_call.get("args", {})
                        })
            
    #Final event indicating completion
    yield format_sse_event({"type": "done"})


def format_sse_event(data: Dict[str, Any]) -> str:
    """
    Format data as server-sent event.

    SSE format:
        data: {json}

        (blank line)

    Args:
        data: Dictionary to send as event
    
    Returns:
        SSE-formatted string
    """
    return f"data: {json.dumps(data)}\n\n"

async def stream_response_content(
    graph,
    messages: list,
    session_id: str,
    customer_name: str = "Guest"
) -> AsyncIterator[str]:
    """
    Simplified streaming: only yield final content_chunks.

    Use when you don't need intermediate node updates,
    just the final response text as it's generated.

    Args:
        graph: Compiled graph
        messages: Input messages
        session_id: Session identifier
        customer_name: User's name

    Yields:
        Content strings (deltas)
    """
    config = {
        "configurable": {"thread_id": session_id}
    }
    
    input_data = {
        "messages": messages,
        "session_id": session_id,
        "customer_name": customer_name,
        "intent": "",
        "tool_call_count": 0,
        "made_tool_calls": False,
    }

    buffer = ""

    async for event in graph.astream(input_data, config):
        for node_name, node_output in event.items():
            if node_name not in ["search_agent", "chat_agent"]:
                continue

            messages_out = node_output.get("messages", [])

            if messages_out:
                last_msg = messages_out[-1]
                content = getattr(last_msg, 'content', None)

                if content and content != buffer:
                    cleaned_content = re.sub(
                        r'<thinking>.*?</thinking>\s*',
                        '',
                        content,
                        flags=re.DOTALL
                    )

                    # Calculate delta from cleaned content
                    if cleaned_content != buffer:
                        delta = cleaned_content[len(buffer):]
                        buffer = cleaned_content
                        
                        if delta:
                            yield delta
