"""OAuth 2.1 configuration for MCP server."""

import os
from typing import Dict, Any, Optional


class OAuthConfig:
    """OAuth 2.1 configuration and metadata."""
    
    def __init__(self, issuer: str, token_store_path: str = None, token_expiry_hours: int = 24,
                 storage_type: str = None, dynamodb_table_name: str = None):
        """Initialize OAuth configuration.
        
        Args:
            issuer: OAuth issuer URL (e.g., 'https://mcp.mycompany.com')
            token_store_path: Path to token storage file (for JSON storage)
            token_expiry_hours: Token expiration time in hours
            storage_type: "json" or "dynamodb". Auto-detected from environment if None.
            dynamodb_table_name: DynamoDB table name (for DynamoDB storage)
        """
        self.issuer = issuer
        self.token_store_path = token_store_path
        self.token_expiry_hours = token_expiry_hours
        
        # Determine storage configuration
        self.storage_type = storage_type or os.environ.get('OAUTH_STORAGE_TYPE', 'json').lower()
        self.dynamodb_table_name = (
            dynamodb_table_name or 
            os.environ.get('OAUTH_TOKENS_TABLE') or
            os.environ.get('DYNAMODB_TABLE_NAME')
        )
        
        # Set default token store path if using JSON storage
        if self.storage_type == 'json' and not self.token_store_path:
            self.token_store_path = 'mcp_oauth_tokens.json'
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration for token store creation.
        
        Returns:
            Dictionary with storage configuration parameters
        """
        config = {"storage_type": self.storage_type}
        
        if self.storage_type == 'json':
            config["file_path"] = self.token_store_path
        elif self.storage_type == 'dynamodb':
            config["table_name"] = self.dynamodb_table_name
            config["region_name"] = os.environ.get('AWS_REGION')
        
        return config
    
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