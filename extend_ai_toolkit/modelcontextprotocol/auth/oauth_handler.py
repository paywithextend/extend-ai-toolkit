"""OAuth 2.1 authentication handler for MCP server."""

from typing import Optional
from datetime import datetime, timedelta

from ..storage.base import TokenStore, TokenData
from ...shared.oauth_config import OAuthConfig
from .auth_code_store import AuthCodeStore, AuthCodeData
from .crypto_utils import (
    generate_secure_token, 
    generate_authorization_code,
    verify_pkce_challenge,
    simple_encrypt,
    simple_decrypt
)


class OAuthHandler:
    """Handles OAuth 2.1 authentication flow for MCP server."""
    
    def __init__(self, oauth_config: OAuthConfig, token_store: TokenStore):
        """Initialize OAuth handler.
        
        Args:
            oauth_config: OAuth configuration
            token_store: Token storage implementation
        """
        self.oauth_config = oauth_config
        self.token_store = token_store
        self.auth_code_store = AuthCodeStore("mcp_auth_codes.json")
        self._encryption_key = "mcp_oauth_key_2024"  # Simple key for PoC
    
    async def validate_bearer_token(self, token: str) -> Optional[TokenData]:
        """Validate Bearer token and return user context.
        
        Args:
            token: Bearer token from Authorization header
            
        Returns:
            TokenData if valid, None if invalid/expired
        """
        if not token or not token.startswith("oauth_"):
            return None
        
        token_data = await self.token_store.get_token(token)
        if not token_data:
            return None
        
        if token_data.is_expired():
            # Clean up expired token
            await self.token_store.delete_token(token)
            return None
        
        # Decrypt API credentials if they were encrypted
        if token_data.extend_api_key and token_data.extend_api_secret:
            token_data.extend_api_key = simple_decrypt(token_data.extend_api_key, self._encryption_key)
            token_data.extend_api_secret = simple_decrypt(token_data.extend_api_secret, self._encryption_key)
        
        return token_data
    
    async def generate_authorization_code(self, user_email: str, extend_api_key: str, 
                                        extend_api_secret: str, code_challenge: str,
                                        code_challenge_method: str = "S256",
                                        client_id: str = None, redirect_uri: str = None,
                                        state: str = None) -> str:
        """Generate authorization code for OAuth flow.
        
        Args:
            user_email: User's email address
            extend_api_key: User's Extend API key
            extend_api_secret: User's Extend API secret
            code_challenge: PKCE code challenge
            code_challenge_method: PKCE challenge method (S256 or plain)
            client_id: OAuth client ID
            redirect_uri: OAuth redirect URI
            state: OAuth state parameter
            
        Returns:
            Authorization code string
        """
        # Generate authorization code
        auth_code = generate_authorization_code()
        
        # Encrypt API credentials for storage
        encrypted_api_key = simple_encrypt(extend_api_key, self._encryption_key)
        encrypted_api_secret = simple_encrypt(extend_api_secret, self._encryption_key)
        
        # Store authorization code data
        auth_code_data = AuthCodeData(
            code=auth_code,
            user_email=user_email,
            extend_api_key=encrypted_api_key,
            extend_api_secret=encrypted_api_secret,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            client_id=client_id,
            redirect_uri=redirect_uri,
            state=state
        )
        
        await self.auth_code_store.store_auth_code(auth_code_data)
        
        return auth_code
    
    async def exchange_code_for_token(self, auth_code: str, code_verifier: str,
                                    client_id: str = None, redirect_uri: str = None) -> dict:
        """Exchange authorization code for access token.
        
        Args:
            auth_code: Authorization code from OAuth flow
            code_verifier: PKCE code verifier
            client_id: OAuth client ID (optional verification)
            redirect_uri: OAuth redirect URI (optional verification)
            
        Returns:
            Token response dict with access_token, token_type, expires_in
            
        Raises:
            ValueError: If code is invalid, expired, or PKCE verification fails
        """
        # Get authorization code data
        auth_data = await self.auth_code_store.get_auth_code(auth_code)
        if not auth_data:
            raise ValueError("Invalid authorization code")
        
        if auth_data.is_expired():
            # Clean up expired code
            await self.auth_code_store.delete_auth_code(auth_code)
            raise ValueError("Authorization code expired")
        
        # Verify PKCE challenge
        if not verify_pkce_challenge(code_verifier, auth_data.code_challenge, auth_data.code_challenge_method):
            raise ValueError("Invalid PKCE code verifier")
        
        # Optional client_id verification
        if client_id and auth_data.client_id and client_id != auth_data.client_id:
            raise ValueError("Client ID mismatch")
        
        # Optional redirect_uri verification
        if redirect_uri and auth_data.redirect_uri and redirect_uri != auth_data.redirect_uri:
            raise ValueError("Redirect URI mismatch")
        
        # Generate access token
        access_token = generate_secure_token()
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(hours=self.oauth_config.token_expiry_hours)
        
        # Store token mapping
        token_data = TokenData(
            token=access_token,
            user_email=auth_data.user_email,
            extend_api_key=auth_data.extend_api_key,  # Already encrypted
            extend_api_secret=auth_data.extend_api_secret,  # Already encrypted
            expires_at=expires_at.isoformat()
        )
        
        await self.token_store.store_token(token_data)
        
        # Clean up authorization code (one-time use)
        await self.auth_code_store.delete_auth_code(auth_code)
        
        # Return token response
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": int(self.oauth_config.token_expiry_hours * 3600),
            "scope": "mcp"
        }
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke an access token.
        
        Args:
            token: Access token to revoke
            
        Returns:
            True if token was revoked, False if token didn't exist
        """
        return await self.token_store.delete_token(token)
    
    async def cleanup_expired_data(self) -> dict:
        """Clean up expired tokens and authorization codes.
        
        Returns:
            Dict with cleanup statistics
        """
        expired_tokens = await self.token_store.cleanup_expired_tokens()
        expired_codes = await self.auth_code_store.cleanup_expired_codes()
        
        return {
            "expired_tokens_cleaned": expired_tokens,
            "expired_codes_cleaned": expired_codes
        }