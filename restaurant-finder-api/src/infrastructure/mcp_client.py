"""MCP Client using AWS AgentCore Gateway - Real MCP Protocol."""
import logging
import json
from typing import List, Dict, Any, Optional
import urllib.request
import urllib.error

import boto3
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

from src.config import settings
from src.domain.models import Restaurant

logger = logging.getLogger(__name__)


class AgentCoreMCPClient:
    """
    Real MCP client using AWS AgentCore Gateway.
    Calls Gateway's /mcp endpoint using MCP protocol (JSON-RPC over HTTP)
    with sigV4 IAM authentication.
    """
    
    def __init__(
            self,
            gateway_url: Optional[str]=None
            ):
        """Initialize MCP client with AgentCore Gateway."""
        self.gateway_url = gateway_url or settings.GATEWAY_URL

        if not self.gateway_url:
            raise ValueError("GATEWAY_URL not set in environment")
        
        # Get AWS session for SigV4 signing
        if settings.AWS_PROFILE:
            session = boto3.Session(profile_name=settings.AWS_PROFILE)
        else:
            session = boto3.Session()

        self._credentials = session.get_credentials().get_frozen_credentials()
        self._region = settings.AWS_REGION
        logger.info(f"AgentCore MCP Client intialized: {self.gateway_url}")

    def _signed_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make SigV4-signed POST to AgentCore Gateway MCP endpoint.
        The Gateway accepts MCP JSON-RPC protocol over HTTP POST.
        """
        body = json.dumps(payload).encode("utf-8")

        # Build AWS request for signing
        request = AWSRequest(
            method="POST",
            url=self.gateway_url,
            data=body,
            headers={"Content-Type": "application/json"},
        )

        # Sign with SigV4
        SigV4Auth(
            self._credentials,
            "bedrock-agentcore",
            self._region
        ).add_auth(request)

        # Execute the signed HTTP request
        prepared = request.prepare()
        http_req = urllib.request.Request(
            prepared.url,
            data=body,
            headers=dict(prepared.headers),
            method="POST"
        )

        with urllib.request.urlopen(http_req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))


    def invoke_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Invoke a tool via MCP protocol (JSON-RPC call/tool).
        MCP uses JSON-RPC 2.0 format over HTTP POST.
        """
        # MCP JSON-RPC request format
        payload = {
            "jsonrpc": "2.0",
            "id":1,
            "method": "tools/call",
            "params": {
                "name": "target-quick-start-bvi1nk___"+tool_name,
                "arguments": parameters
            },
        }
        
        try:
            response = self._signed_request(payload)

            # MCP resposne format: {"jsonrpc": "2.0", "id":1, "result":{....}}
            if "error" in response:
                logger.error(f"MCP error: {response['error']}")
                return {"status": "error", "message": response["error"].get("message")}
            
            # The result from the lambda is stored isnide response["result"]
            result = response.get("result", {})
            logger.debug(f"Raw MCP result: {json.dumps(result)}")
            # MCP standard: Lambda result is nested inside content[0].text
            content_items = result.get("content", [])
            if content_items and isinstance(content_items, list):
                text = next(
                    (c.get("text") for c in content_items if c.get("type") == "text"),
                    None
                )
                if text:
                    parsed = json.loads(text)
                    # Lambda wraps in {"statusCode": ..., "body": "...json string..."}
                    if "body" in parsed:
                        return json.loads(parsed["body"])
                    return parsed

            # Fallback for direct body (non-MCP wrapping)
            if "body" in result:
                return json.loads(result["body"])
            
            return result
    
        except urllib.error.HTTPError as e:
            logger.error(f"Gateway HTTP error {e.code}: {e.read()}")
            return {"status":"error", "message": f"HTTP {e.code}"}
        except Exception as e:
            logger.error(f"MCP invocation error: {e}")
            return {"status": "error", "message": str(e)}

    def search_restaurants(
            self,
            location: str,
            cuisine: Optional[str] = None,
            dietary_restrictions: Optional[List[str]] = None,
            max_results: int = 5,
    ) -> List[Restaurant]:
        """
        Search for restaurants via MCP Gateway.

        This calls the Lambda function through AgentCore Gateway
        using real MCP protocol (JSON-RPC over streamable HTTP).
        """
        try:
            # Prepare parameters
            params: Dict[str, Any] = {
                "location": location,
                "max_results": max_results
            }

            if cuisine:
                params["cuisine"] = cuisine

            if dietary_restrictions:
                params["dietary_restrictions"] = ",".join(dietary_restrictions)

            # Invoke via MCP Gateway
            result = self.invoke_tool("search_restaurants", params)

            # Parse response
            if result.get("status") != "success":
                logger.warning(f"Search failed: {result.get('message')}")
                return []
            
            # Convert to Restaurant domain models
            restaurants = []
            for r_data in result.get("restaurants", []):
                try:
                    restaurant = Restaurant(**r_data)
                    restaurants.append(restaurant)
                except Exception as e:
                    logger.warning(f"Failed to parse restaurant: {e}")
                    continue

            logger.info(f"MCP search returned {len(restaurants)} restaurants")
            return restaurants
            

        except Exception as e:
            logger.error(f"Error in search_restaurants: {e}")
            return []
        

# Global MCP client instance
_mcp_client: Optional[AgentCoreMCPClient] = None

def get_mcp_client() -> AgentCoreMCPClient:
    """Get or create MCP client singleton."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client =AgentCoreMCPClient()
    return _mcp_client

