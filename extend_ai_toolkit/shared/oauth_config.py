"""OAuth 2.1 configuration for MCP server."""

from typing import Dict, Any


class OAuthConfig:
    """OAuth 2.1 configuration and metadata."""
    
    def __init__(self, issuer: str, token_store_path: str, token_expiry_hours: int = 24):
        """Initialize OAuth configuration.
        
        Args:
            issuer: OAuth issuer URL (e.g., 'https://mcp.mycompany.com')
            token_store_path: Path to token storage file
            token_expiry_hours: Token expiration time in hours
        """
        self.issuer = issuer
        self.token_store_path = token_store_path
        self.token_expiry_hours = token_expiry_hours
    
    def get_protected_resource_metadata(self) -> Dict[str, Any]:
        """Return OAuth 2.1 protected resource metadata.
        
        This is served at /.well-known/oauth-protected-resource
        """
        return {
            "authorization_servers": [
                {
                    "issuer": self.issuer,
                    "authorization_endpoint": f"{self.issuer}/authorize",
                }
            ]
        }
    
    def get_authorization_server_metadata(self) -> Dict[str, Any]:
        """Return OAuth 2.1 authorization server metadata.
        
        This is served at /.well-known/oauth-authorization-server
        """
        return {
            "issuer": self.issuer,
            "authorization_endpoint": f"{self.issuer}/authorize",
            "token_endpoint": f"{self.issuer}/token",
            "registration_endpoint": f"{self.issuer}/register",
            "token_endpoint_auth_methods_supported": ["none"],
            "scopes_supported": ["mcp"],
            "response_types_supported": ["code"],
            "response_modes_supported": ["query"],
            "grant_types_supported": ["authorization_code"],
            "code_challenge_methods_supported": ["S256"]
        }
    
    @property
    def authorization_endpoint(self) -> str:
        """OAuth authorization endpoint URL."""
        return f"{self.issuer}/authorize"
    
    @property
    def token_endpoint(self) -> str:
        """OAuth token endpoint URL."""
        return f"{self.issuer}/token"
    
    @property
    def callback_endpoint(self) -> str:
        """OAuth callback endpoint URL."""
        return f"{self.issuer}/callback"