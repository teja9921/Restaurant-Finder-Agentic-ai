#restaurant-finder-api/src/infrastructure/mcp_client.py
"""MCP Gateway client - Mock version for Sprint 3."""
import json
from typing import Dict, Any, Optional
from src.config import settings


class MCPClient:
    """Client for MCP Gateway communication - Mock implementation."""
    
    def __init__(self):
        """Initialize MCP client."""
        self.gateway_url = getattr(settings, 'GATEWAY_URL', None)
        # Mock mode if no gateway configured
        self.mock_mode = not self.gateway_url
    
    def call_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call tool through MCP Gateway.
        
        """
        if self.mock_mode or True:  
            return self._mock_tool_call(tool_name, parameters)
    
    def _mock_tool_call(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock tool execution."""
        if tool_name == "search_restaurants":
            location = parameters.get("location", "Unknown")
            cuisine = parameters.get("cuisine")
            
            mock_results = [
                {
                    "name": "Bella Italia",
                    "cuisine": "Italian",
                    "location": location,
                    "rating": 4.5,
                    "price_level": "$$",
                },
                {
                    "name": "Spice Garden",
                    "cuisine": "Indian",
                    "location": location,
                    "rating": 4.3,
                    "price_level": "$",
                },
            ]
            
            # Filter by cuisine
            if cuisine:
                mock_results = [
                    r for r in mock_results
                    if cuisine.lower() in r["cuisine"].lower()
                ]
            
            return {"restaurants": mock_results}
        
        return {"error": f"Unknown tool: {tool_name}"}


# Global instance
mcp_client = MCPClient()