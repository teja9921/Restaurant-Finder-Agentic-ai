"""Agent tools using MCP client"""
import json
from typing import Optional
from langchain_core.tools import tool
from src.infrastructure.mcp_client import mcp_client
from src.domain.models import Restaurant, SearchResult


@tool
def search_restaurants(
    location: str,
    cuisine: Optional[str] = None,
    price_level: Optional[str] = None
) -> str:
    """
    Search for restaurants using MCP Gateway.
    
    Args:
        location: City or area to search in
        cuisine: Type of cuisine (Italian, Chinese, etc.)
        price_level: Price range ($, $$, $$$, $$$$)

    Returns:
        JSON string with restaurant results
    """
    #Call MCP client
    result = mcp_client.call_tool(
        tool_name = "search_restaurants",
        parameters ={
            "location": location,
            "cuisine": cuisine,
            "price_level": price_level,
        }
    )

    #Parse into domain models
    restaurants = [
        Restaurant(**r)
        for r in result.get("restaurants", [])
    ]

    search_result = SearchResult(
        query = f"{cuisine or 'restaurants'} in {location}",
        restaurants = restaurants,
        total_results = len(restaurants)
    )

    return search_result.model_dump_json()

# Tools list
ALL_TOOLS = [search_restaurants]