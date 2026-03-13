"""
Lambda handler for restaurant search tool.
Implements MCP-compatible tool that calls SearchAPI.io
"""
import json
import os 
import logging
from typing import Dict, Any, Optional, List
import urllib.request
import urllib.parse
import urllib.error
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Intialize Secrets Manager client
secrets_client = boto3.client('secretsmanager')
_api_key_cache = None


def get_searchapi_key() -> str:
    """Get SearchAPI key from Secrets Manager with caching."""
    global _api_key_cache

    if _api_key_cache:
        return _api_key_cache
    
    try:
        secret_arn = os.environ.get("SEARCHAPI_SECRET_ARN")
        if not secret_arn:
            raise ValueError("SEARCHAPI_SECRET_ARN not set")
        
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        _api_key_cache = response['SecretString']
        return _api_key_cache
    
    except ClientError as e:
        logger.error(f"Error retrieving secret: {e}")
        raise


def search_restaurants(
        location: str,
    cuisine: Optional[str] = None,
    dietary_restrictions: Optional[str] = None,
        max_results: int = 5
) -> Dict[str, Any]:
    """
    Search for restaurants using SearchAPI.io Google Local engine.

    Args:
        location: City or area to search
        cuisine: Type of cuisine (optional)
        dietary_restrictions: Comma-separated dietary needs (optional)
        max_results: Maximum results to return
        
    Returns:
        Dictionary with restaurant results
    """
    try: 
        # Get API key from Secrets Manager.
        _api_key = get_searchapi_key()

        # Build search query
        query  = f"restaurants in {location}"
        if cuisine:
            query = f"{cuisine} {query}"
        if dietary_restrictions:
            restrictions = dietary_restrictions.replace(",", " ")
            query = f"{restrictions} {query}"

        # Build SearchAPI
        params = {
            "engine": "google_maps",
            "q": query,
            "type": "search",
            "api_key": _api_key,
            "num": str(max_results)
        }

        url = f"https://www.searchapi.io/api/v1/search?{urllib.parse.urlencode(params)}"

        # Make request
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())

        # Parse results
        local_results = data.get("local_results", [])

        restaurants: List[Dict[str, Any]] = []
        for result in local_results[:max_results]:
            try: 
                restaurant = {
                    "name": result.get("title", "Unknown"),
                    "address": result.get("address", "No address available"),
                    "rating": float(result.get("rating")),
                    "cuisine": cuisine or result.get("type", "Various"),
                    "price_level": result.get("price", "$$"),
                    "phone": result.get("phone"),
                    "website": result.get("website"),
                    "opening_hours": result.get("hours"),
                    "review_count": result.get("reviews", 0)
                }     
                restaurants.append(restaurant)
            except Exception as e:
                logger.warning(f"Failed to parse restaurant: {e}")
                continue

        return {
            "status": "success",
            "count": len(restaurants),
            "location": location,
            "cuisine": cuisine,
            "dietary_restrictions": dietary_restrictions,
            "restaurants": restaurants
        }

    except urllib.error.HTTPError as e:
        logger.error(f"SearchAPI HTTP error: {e}")
        return  {
            "status":"error",
            "message": str(e),
            "restaurants": []
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for AgentCore Gateway MCP integration.
    
    Event format from AgentCore Gateway;
    {
        "tool": "search_restaurants",
        "parameters": {
            "location": "Mumbai",
            "cuisine": "Italian",
            "dietary_restrictions": "vegan",
            "max_results": 5
        }
    }
    """
    try: 
        logger.info(f"Received event: {json.dumps(event)}")

        # Extract tool name and parameters
        tool_name = event.get("tool", "search_restaurants")
        parameters = event.get("parameters", {})

        # Accept camelCase from tool schema while keeping Python internals snake_case.
        normalized_parameters = {
            "location": parameters.get("location"),
            "cuisine": parameters.get("cuisine"),
            "dietary_restrictions": parameters.get(
                "dietary_restrictions",
                parameters.get("dietaryRestrictions")
            ),
            "max_results": parameters.get(
                "max_results",
                parameters.get("maxResults", 5)
            ),
        }

        # Route to appropriate tool
        if tool_name == "search_restaurants":
            result = search_restaurants(**normalized_parameters)
        else:
            result = {
                "status": "error",
                "message": f"Unknown tool: {tool_name}"
            }

        # Return result
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }

    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e)
            })
        }