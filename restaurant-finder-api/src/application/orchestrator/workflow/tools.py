"""Agent tools using MCP client"""
import json
from typing import Optional
from langchain_core.tools import tool
from src.infrastructure.mcp_client import get_mcp_client
from src.domain.models import Restaurant, SearchResult


@tool
def search_restaurants(
    location: str,
    cuisine: Optional[str] = None,
    dietary_restrictions: Optional[str] = None
) -> str:
    """
    Search for restaurants using MCP Gateway.
    
    Args:
        location: City or area to search in
        cuisine: Type of cuisine (Italian, Chinese, etc.)
        dietary_restrictions: 'Vegan', 'Vegetarian' , 'Non-Vegetarian'

    Returns:
        JSON string with restaurant results
    """
    #get mcp client
    mcp_client = get_mcp_client()
    restaurants = mcp_client.search_restaurants(
            location,
            cuisine,
            dietary_restrictions,
    )

    search_result = SearchResult(
        query = f"{cuisine or 'restaurants'} in {location}",
        restaurants = restaurants,
        total_results = len(restaurants)
    )

    return search_result.model_dump_json()

# Tools list
ALL_TOOLS = [search_restaurants]