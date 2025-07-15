"""OAuth 2.1 endpoints for MCP server using Starlette."""

import logging
from typing import List
from urllib.parse import urlparse, parse_qs

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from starlette.exceptions import HTTPException

from extend import ExtendClient
from .auth.oauth_handler import OAuthHandler
from ..shared.oauth_config import OAuthConfig

logger = logging.getLogger(__name__)

# Templates will be initialized when creating routes
templates = None


def get_base_url(request: Request) -> str:
    """Extract base URL from request."""
    scheme = request.url.scheme
    host = request.headers.get("host", request.url.netloc)
    return f"{scheme}://{host}"


class OAuthEndpoints:
    """OAuth 2.1 endpoint handlers."""
    
    def __init__(self, oauth_handler: OAuthHandler, oauth_config: OAuthConfig):
        self.oauth_handler = oauth_handler
        self.oauth_config = oauth_config
    
    async def protected_resource_metadata(self, request: Request) -> JSONResponse:
        """OAuth 2.1 protected resource metadata (/.well-known/oauth-protected-resource)."""
        try:
            # Use actual request URL for issuer if not configured
            base_url = get_base_url(request)
            config_with_base = OAuthConfig(
                issuer=base_url,
                token_store_path=self.oauth_config.token_store_path,
                token_expiry_hours=self.oauth_config.token_expiry_hours
            )
            
            metadata = config_with_base.get_protected_resource_metadata()
            return JSONResponse(metadata)
        except Exception as e:
            logger.error(f"Error serving protected resource metadata: {e}")
            return JSONResponse({"error": "server_error"}, status_code=500)
    
    async def authorization_server_metadata(self, request: Request) -> JSONResponse:
        """OAuth 2.1 authorization server metadata (/.well-known/oauth-authorization-server)."""
        try:
            # Use actual request URL for issuer if not configured
            base_url = get_base_url(request)
            config_with_base = OAuthConfig(
                issuer=base_url,
                token_store_path=self.oauth_config.token_store_path,
                token_expiry_hours=self.oauth_config.token_expiry_hours
            )
            
            metadata = config_with_base.get_authorization_server_metadata()
            return JSONResponse(metadata)
        except Exception as e:
            logger.error(f"Error serving authorization server metadata: {e}")
            return JSONResponse({"error": "server_error"}, status_code=500)
    
    async def authorize_endpoint(self, request: Request) -> HTMLResponse:
        """OAuth 2.1 authorization endpoint (/authorize)."""
        try:
            # Extract OAuth parameters
            client_id = request.query_params.get("client_id")
            redirect_uri = request.query_params.get("redirect_uri")
            code_challenge = request.query_params.get("code_challenge")
            code_challenge_method = request.query_params.get("code_challenge_method", "S256")
            state = request.query_params.get("state")
            response_type = request.query_params.get("response_type")
            scope = request.query_params.get("scope", "mcp")
            
            # Validate required parameters
            if not response_type:
                return HTMLResponse("Missing response_type parameter", status_code=400)
            
            if response_type != "code":
                return HTMLResponse("Unsupported response_type. Only 'code' is supported.", status_code=400)
            
            if not client_id:
                return HTMLResponse("Missing client_id parameter", status_code=400)
            
            if not redirect_uri:
                return HTMLResponse("Missing redirect_uri parameter", status_code=400)
            
            if not code_challenge:
                return HTMLResponse("Missing code_challenge parameter (PKCE required)", status_code=400)
            
            # Validate redirect_uri format
            try:
                parsed_uri = urlparse(redirect_uri)
                if not parsed_uri.scheme or not parsed_uri.netloc:
                    return HTMLResponse("Invalid redirect_uri format", status_code=400)
            except Exception:
                return HTMLResponse("Invalid redirect_uri format", status_code=400)
            
            # Serve login page with OAuth parameters
            global templates
            if not templates:
                # Fallback if templates not initialized
                return HTMLResponse(f"""
                <html>
                <head><title>Extend MCP OAuth Login</title></head>
                <body>
                    <h2>Extend MCP Server - OAuth Login</h2>
                    <p>Login page template will be implemented in Step 5.</p>
                    <p>OAuth parameters received:</p>
                    <ul>
                        <li>client_id: {client_id}</li>
                        <li>redirect_uri: {redirect_uri}</li>
                        <li>code_challenge: {code_challenge[:20]}...</li>
                        <li>state: {state}</li>
                    </ul>
                </body>
                </html>
                """)
            
            return templates.TemplateResponse("oauth_login.html", {
                "request": request,
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method,
                "state": state,
                "scope": scope
            })
            
        except Exception as e:
            logger.error(f"Error in authorize endpoint: {e}")
            return HTMLResponse("Internal server error", status_code=500)
    
    async def callback_endpoint(self, request: Request) -> RedirectResponse:
        """OAuth callback endpoint (/callback) - handles login form submission."""
        try:
            form = await request.form()
            
            # Extract user credentials
            user_email = form.get("user_email")
            extend_api_key = form.get("extend_api_key")
            extend_api_secret = form.get("extend_api_secret")
            
            # Extract OAuth parameters
            client_id = form.get("client_id")
            redirect_uri = form.get("redirect_uri")
            code_challenge = form.get("code_challenge")
            code_challenge_method = form.get("code_challenge_method", "S256")
            state = form.get("state")
            
            # Validate required fields
            if not all([user_email, extend_api_key, extend_api_secret, redirect_uri, code_challenge]):
                return HTMLResponse("Missing required fields", status_code=400)
            
            # Validate Extend API credentials with test call
            try:
                test_client = ExtendClient(api_key=extend_api_key, api_secret=extend_api_secret)
                # Make a simple test call to validate credentials
                await test_client.virtual_cards.get_virtual_cards(per_page=1)
                logger.info(f"Successfully validated credentials for user: {user_email}")
            except Exception as e:
                logger.warning(f"Invalid Extend API credentials for {user_email}: {e}")
                return HTMLResponse(f"Invalid Extend API credentials. Please check your API key and secret. Error: {str(e)}", status_code=400)
            
            # Generate authorization code
            auth_code = await self.oauth_handler.generate_authorization_code(
                user_email=user_email,
                extend_api_key=extend_api_key,
                extend_api_secret=extend_api_secret,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method,
                client_id=client_id,
                redirect_uri=redirect_uri,
                state=state
            )
            
            # Build redirect URL with authorization code
            redirect_url = f"{redirect_uri}?code={auth_code}"
            if state:
                redirect_url += f"&state={state}"
            
            logger.info(f"Generated authorization code for {user_email}, redirecting to {redirect_uri}")
            return RedirectResponse(redirect_url, status_code=302)
            
        except Exception as e:
            logger.error(f"Error in callback endpoint: {e}")
            return HTMLResponse("Internal server error during authentication", status_code=500)
    
    async def token_endpoint(self, request: Request) -> JSONResponse:
        """OAuth token endpoint (/token) - exchanges authorization code for access token."""
        try:
            form = await request.form()
            
            # Extract token request parameters
            grant_type = form.get("grant_type")
            code = form.get("code")
            code_verifier = form.get("code_verifier")
            client_id = form.get("client_id")
            redirect_uri = form.get("redirect_uri")
            
            # Validate grant type
            if grant_type != "authorization_code":
                return JSONResponse({
                    "error": "unsupported_grant_type",
                    "error_description": "Only authorization_code grant type is supported"
                }, status_code=400)
            
            # Validate required parameters
            if not code:
                return JSONResponse({
                    "error": "invalid_request",
                    "error_description": "Missing authorization code"
                }, status_code=400)
            
            if not code_verifier:
                return JSONResponse({
                    "error": "invalid_request", 
                    "error_description": "Missing PKCE code_verifier"
                }, status_code=400)
            
            # Exchange authorization code for access token
            try:
                token_response = await self.oauth_handler.exchange_code_for_token(
                    auth_code=code,
                    code_verifier=code_verifier,
                    client_id=client_id,
                    redirect_uri=redirect_uri
                )
                
                logger.info(f"Successfully exchanged authorization code for access token")
                return JSONResponse(token_response)
                
            except ValueError as e:
                logger.warning(f"Token exchange failed: {e}")
                return JSONResponse({
                    "error": "invalid_grant",
                    "error_description": str(e)
                }, status_code=400)
                
        except Exception as e:
            logger.error(f"Error in token endpoint: {e}")
            return JSONResponse({
                "error": "server_error",
                "error_description": "Internal server error"
            }, status_code=500)
    
    async def revoke_endpoint(self, request: Request) -> JSONResponse:
        """OAuth token revocation endpoint (/revoke)."""
        try:
            form = await request.form()
            token = form.get("token")
            
            if not token:
                return JSONResponse({
                    "error": "invalid_request",
                    "error_description": "Missing token parameter"
                }, status_code=400)
            
            # Revoke the token
            revoked = await self.oauth_handler.revoke_token(token)
            
            if revoked:
                logger.info(f"Successfully revoked token")
            else:
                logger.info(f"Token revocation requested for non-existent token")
            
            # OAuth spec says to return 200 even if token didn't exist
            return JSONResponse({"revoked": True})
            
        except Exception as e:
            logger.error(f"Error in revoke endpoint: {e}")
            return JSONResponse({
                "error": "server_error",
                "error_description": "Internal server error"
            }, status_code=500)
    
    async def register_endpoint(self, request: Request) -> JSONResponse:
        """OAuth client registration endpoint (/register) - simplified for PoC."""
        try:
            # For PoC, we'll just return a simple response
            # In production, this would handle dynamic client registration
            
            body = await request.json() if request.headers.get("content-type") == "application/json" else {}
            client_name = body.get("client_name", "MCP Client")
            
            # Generate a simple client_id for the PoC
            import secrets
            client_id = f"mcp_client_{secrets.token_hex(8)}"
            
            response = {
                "client_id": client_id,
                "client_name": client_name,
                "token_endpoint_auth_method": "none",
                "grant_types": ["authorization_code"],
                "response_types": ["code"]
            }
            
            logger.info(f"Registered new OAuth client: {client_id}")
            return JSONResponse(response, status_code=201)
            
        except Exception as e:
            logger.error(f"Error in register endpoint: {e}")
            return JSONResponse({
                "error": "server_error",
                "error_description": "Internal server error"
            }, status_code=500)


def create_oauth_routes(oauth_handler: OAuthHandler, oauth_config: OAuthConfig, 
                       templates_instance: Jinja2Templates = None) -> List[Route]:
    """Create OAuth route handlers.
    
    Args:
        oauth_handler: OAuth authentication handler
        oauth_config: OAuth configuration
        templates_instance: Jinja2 templates instance (optional)
        
    Returns:
        List of Starlette routes
    """
    global templates
    templates = templates_instance
    
    endpoints = OAuthEndpoints(oauth_handler, oauth_config)
    
    return [
        Route("/.well-known/oauth-protected-resource", 
              endpoints.protected_resource_metadata, methods=["GET"]),
        Route("/.well-known/oauth-authorization-server", 
              endpoints.authorization_server_metadata, methods=["GET"]),
        Route("/authorize", endpoints.authorize_endpoint, methods=["GET"]),
        Route("/callback", endpoints.callback_endpoint, methods=["POST"]),
        Route("/token", endpoints.token_endpoint, methods=["POST"]),
        Route("/revoke", endpoints.revoke_endpoint, methods=["POST"]),
        Route("/register", endpoints.register_endpoint, methods=["POST"]),
    ]