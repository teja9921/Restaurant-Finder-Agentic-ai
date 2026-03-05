"""Agent tools - Mock version."""
from typing import List
from langchain_core.tools import tool
from src.domain.models import Restaurant


@tool
def search_restaurants(
    location: str,
    cuisine: str = None,
) -> str:
    """
    Search for restaurants matching criteria.
    
    Args:
        location: City or area to search in
        cuisine: Type of cuisine (Italian, Chinese, etc.)
    
    Returns:
        JSON string with restaurant results
    """
    # Mock data for testing
    mock_restaurants = [
        Restaurant(
            name="Bella Italia",
            cuisine="Italian",
            location=location,
        ),
        Restaurant(
            name="Dragon Palace",
            cuisine="Chinese", 
            location=location,
        ),
        Restaurant(
            name="Taco Fiesta",
            cuisine="Mexican",
            location=location,
        ),
    ]
    
    # Filter by cuisine if provided
    if cuisine:
        mock_restaurants = [
            r for r in mock_restaurants 
            if r.cuisine and cuisine.lower() in r.cuisine.lower()
        ]
    
    # Convert to JSON
    results = [r.model_dump() for r in mock_restaurants]
    
    import json
    return json.dumps({"restaurants": results})


# Tools list
ALL_TOOLS = [search_restaurants]