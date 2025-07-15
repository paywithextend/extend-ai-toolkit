"""Authentication middleware for MCP requests."""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MCPAuthenticationError(Exception):
    """Exception for MCP authentication failures."""
    
    def __init__(self, error_code: int, message: str, www_authenticate: str = None):
        self.error_code = error_code
        self.message = message
        self.www_authenticate = www_authenticate
        super().__init__(message)
    
    def to_mcp_error(self, request_id: Any = None) -> Dict[str, Any]:
        """Convert to MCP-compliant error response."""
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": self.error_code,
                "message": self.message
            },
            "id": request_id
        }
        
        if self.www_authenticate:
            error_response["error"]["data"] = {
                "www_authenticate": self.www_authenticate
            }
        
        return error_response


class MCPAuthMiddleware:
    """Middleware for handling MCP authentication."""
    
    def __init__(self, mcp_server):
        self.mcp_server = mcp_server
    
    async def authenticate_mcp_request(self, request, request_body: Dict[str, Any] = None) -> Optional[str]:
        """Authenticate MCP request and set user context.
        
        Args:
            request: HTTP request object
            request_body: Parsed MCP request body
            
        Returns:
            None if authentication successful, error response string if failed
            
        Raises:
            MCPAuthenticationError: If authentication fails
        """
        if not self.mcp_server.oauth_handler:
            # API key mode - no authentication needed
            return None
        
        # OAuth mode - require Bearer token
        user_context = await self.mcp_server.authenticate_request(request)
        
        if not user_context:
            # Missing or invalid token
            base_url = self._get_base_url(request)
            www_authenticate = f'Bearer realm="MCP Server", resource_metadata_uri="{base_url}/.well-known/oauth-protected-resource"'
            
            raise MCPAuthenticationError(
                error_code=-32001,
                message="Authentication required",
                www_authenticate=www_authenticate
            )
        
        # Set user context for this request
        self.mcp_server.set_user_context(user_context)
        return None
    
    def _get_base_url(self, request) -> str:
        """Extract base URL from request."""
        scheme = getattr(request.url, 'scheme', 'https')
        netloc = getattr(request, 'headers', {}).get('host', getattr(request.url, 'netloc', 'localhost'))
        return f"{scheme}://{netloc}"
    
    async def clear_user_context(self) -> None:
        """Clear user context after request processing."""
        self.mcp_server.set_user_context(None)