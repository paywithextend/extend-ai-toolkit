"""Streamable HTTP MCP server with OAuth 2.1 support."""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import uvicorn
from colorama import Fore
from dotenv import load_dotenv
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .server import ExtendMCPServer
from .auth_middleware import MCPAuthMiddleware, MCPAuthenticationError
from .oauth_routes import create_oauth_routes
from .options import Options
from ..shared import Configuration, tools
from ..shared.configuration import VALID_SCOPES

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
mcp_server: Optional[ExtendMCPServer] = None
auth_middleware: Optional[MCPAuthMiddleware] = None


def get_base_url(request: Request) -> str:
    """Extract base URL from request."""
    scheme = request.url.scheme
    host = request.headers.get("host", request.url.netloc)
    return f"{scheme}://{host}"


async def mcp_endpoint(request: Request) -> JSONResponse:
    """Handle MCP requests by processing them through the FastMCP server directly."""
    try:
        # Parse request body
        body = None
        if request.method == "POST":
            try:
                body = await request.json()
            except Exception:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }, status_code=400)
        
        # Authenticate request (OAuth mode only)
        if auth_middleware:
            try:
                await auth_middleware.authenticate_mcp_request(request, body)
            except MCPAuthenticationError as e:
                error_response = e.to_mcp_error(body.get("id") if body else None)
                return JSONResponse(error_response, status_code=401)
        
        # Handle MCP protocol messages directly
        if not body or body.get("jsonrpc") != "2.0":
            return JSONResponse({
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request"},
                "id": body.get("id") if body else None
            }, status_code=400)
        
        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        
        try:
            # Handle MCP methods
            if method == "initialize":
                # Return server capabilities
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "Extend MCP Server",
                            "version": mcp_server.version if hasattr(mcp_server, 'version') else "1.0.0"
                        }
                    },
                    "id": request_id
                }
                
            elif method == "tools/list":
                # List available tools
                tools_list = []
                
                # Try different possible attribute names for tools in FastMCP
                tools_dict = None
                for attr_name in ['tools', '_tools', 'tool_handlers', '_tool_handlers', 'handlers']:
                    if hasattr(mcp_server, attr_name):
                        tools_dict = getattr(mcp_server, attr_name)
                        logger.info(f"Found tools in attribute: {attr_name}")
                        break
                
                if tools_dict:
                    for tool_name, tool_func in tools_dict.items():
                        tool_info = {
                            "name": tool_name,
                            "description": getattr(tool_func, 'description', f"Tool: {tool_name}"),
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                        tools_list.append(tool_info)
                else:
                    # Fallback: use configuration to list expected tools
                    logger.warning("Could not find tools dict, using configuration fallback")
                    for tool in mcp_server.configuration.allowed_tools(tools):
                        tool_info = {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": {
                                "type": "object", 
                                "properties": {},
                                "required": []
                            }
                        }
                        tools_list.append(tool_info)
                
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {"tools": tools_list},
                    "id": request_id
                }
                
            elif method == "tools/call":
                # Call a specific tool
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                # Find the tools dict (same logic as tools/list)
                tools_dict = None
                for attr_name in ['tools', '_tools', 'tool_handlers', '_tool_handlers', 'handlers']:
                    if hasattr(mcp_server, attr_name):
                        tools_dict = getattr(mcp_server, attr_name)
                        break
                
                if tools_dict and tool_name in tools_dict:
                    try:
                        # Call the tool function directly from tools dict
                        tool_func = tools_dict[tool_name]
                        result = await tool_func(**arguments)
                        
                        response_data = {
                            "jsonrpc": "2.0",
                            "result": result,
                            "id": request_id
                        }
                    except Exception as e:
                        logger.error(f"Error calling tool {tool_name}: {e}")
                        response_data = {
                            "jsonrpc": "2.0",
                            "error": {"code": -32603, "message": f"Tool execution error: {str(e)}"},
                            "id": request_id
                        }
                else:
                    # Fallback: find tool in configuration and call via server's tool handling
                    tool_config = None
                    for tool in mcp_server.configuration.allowed_tools(tools):
                        if tool.name == tool_name:
                            tool_config = tool
                            break
                    
                    if not tool_config:
                        response_data = {
                            "jsonrpc": "2.0",
                            "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
                            "id": request_id
                        }
                    else:
                        try:
                            # Call via the server's tool execution mechanism
                            # This will use the server's _handle_tool_request logic
                            extend_api = mcp_server.get_current_extend_api()
                            result = await extend_api.run(tool_config.method.value, **arguments)
                            
                            # Format result as MCP tool response
                            response_data = {
                                "jsonrpc": "2.0",
                                "result": {
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": str(result)
                                        }
                                    ]
                                },
                                "id": request_id
                            }
                        except Exception as e:
                            logger.error(f"Error calling tool {tool_name} via fallback: {e}")
                            response_data = {
                                "jsonrpc": "2.0",
                                "error": {"code": -32603, "message": f"Tool execution error: {str(e)}"},
                                "id": request_id
                            }
            
            else:
                response_data = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": request_id
                }
        
        except Exception as e:
            logger.error(f"Error processing MCP method {method}: {e}")
            response_data = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": request_id
            }
        
        return JSONResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error handling MCP request: {e}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": "Internal server error"},
            "id": None
        }, status_code=500)
    
    finally:
        # Clear user context after request
        if auth_middleware:
            await auth_middleware.clear_user_context()


def create_starlette_app(mcp_server_instance: ExtendMCPServer, oauth_handler=None, oauth_config=None) -> Starlette:
    """Create Starlette application with MCP and OAuth support."""
    global mcp_server, auth_middleware
    
    mcp_server = mcp_server_instance
    auth_middleware = MCPAuthMiddleware(mcp_server) if oauth_handler else None
    
    # Set up templates for OAuth pages
    templates_dir = Path(__file__).parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # Build routes
    routes = []
    
    # Add OAuth routes if in OAuth mode
    if oauth_handler and oauth_config:
        oauth_routes_list = create_oauth_routes(oauth_handler, oauth_config, templates)
        routes.extend(oauth_routes_list)
        logger.info("OAuth routes configured")
    
    # Add MCP endpoint
    routes.append(Route("/mcp", mcp_endpoint, methods=["POST", "DELETE"]))
    
    # Create Starlette app
    app = Starlette(
        routes=routes,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["Mcp-Session-Id", "WWW-Authenticate"]
            )
        ]
    )
    
    return app


def build_server() -> Starlette:
    """Build MCP server from command line arguments."""
    try:
        options = Options.from_args(sys.argv[1:], VALID_SCOPES)
        configuration = Configuration.from_tool_str(options.tools)
        
        logger.info(f"Building server in {options.auth_mode} mode")
        
        if options.auth_mode == "oauth":
            # OAuth mode
            oauth_config = options.get_oauth_config()
            if not oauth_config:
                raise ValueError("OAuth configuration required for OAuth mode")
            
            mcp_server_instance = ExtendMCPServer.oauth_instance(oauth_config, configuration)
            oauth_handler = mcp_server_instance.oauth_handler
            
            logger.info(f"OAuth server configured:")
            logger.info(f"  Issuer: {oauth_config.issuer}")
            logger.info(f"  Token store: {oauth_config.token_store_path}")
            logger.info(f"  Token expiry: {oauth_config.token_expiry_hours} hours")
            
        else:
            # API key mode
            mcp_server_instance = ExtendMCPServer.default_instance(
                options.api_key, options.api_secret, configuration
            )
            oauth_handler = None
            oauth_config = None
            
            logger.info("API key server configured")
        
        # Log available tools
        from ..shared import tools
        allowed_tools = configuration.allowed_tools(tools)
        logger.info(f"Available tools: {[tool.name for tool in allowed_tools]}")
        
        return create_starlette_app(mcp_server_instance, oauth_handler, oauth_config)
        
    except Exception as e:
        logger.error(f"Error building server: {e}")
        raise


def handle_error(error):
    """Handle startup errors."""
    sys.stderr.write(f"\n{Fore.RED}   {str(error)}\n")


if __name__ == "__main__":
    try:
        # Build the server
        app = build_server()
        
        # Get host and port from environment
        host = os.environ.get("MCP_HOST", "127.0.0.1")
        port = int(os.environ.get("MCP_PORT", "8000"))
        
        logger.info(f"Starting Extend MCP server on {host}:{port}")
        logger.info(f"MCP endpoint: http://{host}:{port}/mcp")
        
        if auth_middleware:
            logger.info(f"OAuth endpoints:")
            logger.info(f"  Authorization: http://{host}:{port}/authorize")
            logger.info(f"  Token: http://{host}:{port}/token")
            logger.info(f"  Discovery: http://{host}:{port}/.well-known/oauth-protected-resource")
        
        # Start the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        handle_error(e)
        sys.exit(1)