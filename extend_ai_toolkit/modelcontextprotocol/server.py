import inspect
import logging
from typing import Any, Optional

from mcp.server import FastMCP
from mcp.types import AnyFunction

from extend_ai_toolkit.shared import Configuration
from extend_ai_toolkit.shared import ExtendAPI
from extend_ai_toolkit.shared import ExtendAPITools
from extend_ai_toolkit.shared import functions
from extend_ai_toolkit.shared import tools, Tool
from extend_ai_toolkit.shared.oauth_config import OAuthConfig
from .auth.oauth_handler import OAuthHandler
from .storage.base import TokenStore, TokenData
from ..__version__ import __version__ as _version

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class UserContext:
    """User context for OAuth authenticated requests."""
    
    def __init__(self, token_data: TokenData):
        self.user_email = token_data.user_email
        self.token = token_data.token
        self.extend_api_key = token_data.extend_api_key
        self.extend_api_secret = token_data.extend_api_secret
    
    def create_extend_api(self) -> ExtendAPI:
        """Create user-specific ExtendAPI instance."""
        return ExtendAPI.default_instance(
            api_key=self.extend_api_key,
            api_secret=self.extend_api_secret
        )


class ExtendMCPServer(FastMCP):
    def __init__(self, extend_api: Optional[ExtendAPI], configuration: Configuration, 
                 oauth_handler: Optional[OAuthHandler] = None):
        super().__init__(
            name="Extend MCP Server",
            version=_version
        )

        self._extend = extend_api
        self.oauth_handler = oauth_handler
        self.configuration = configuration
        self._current_user_context: Optional[UserContext] = None

        for tool in configuration.allowed_tools(tools):
            fn: Any = None
            match tool.method.value:
                case ExtendAPITools.GET_VIRTUAL_CARDS.value:
                    fn = functions.get_virtual_cards
                case ExtendAPITools.GET_VIRTUAL_CARD_DETAIL.value:
                    fn = functions.get_virtual_card_detail
                case ExtendAPITools.CANCEL_VIRTUAL_CARD.value:
                    fn = functions.cancel_virtual_card
                case ExtendAPITools.CLOSE_VIRTUAL_CARD.value:
                    fn = functions.close_virtual_card
                case ExtendAPITools.GET_TRANSACTIONS.value:
                    fn = functions.get_transactions
                case ExtendAPITools.GET_TRANSACTION_DETAIL.value:
                    fn = functions.get_transaction_detail
                case ExtendAPITools.GET_CREDIT_CARDS.value:
                    fn = functions.get_credit_cards
                case ExtendAPITools.GET_CREDIT_CARD_DETAIL.value:
                    fn = functions.get_credit_card_detail
                case ExtendAPITools.GET_EXPENSE_CATEGORIES.value:
                    fn = functions.get_expense_categories
                case ExtendAPITools.GET_EXPENSE_CATEGORY.value:
                    fn = functions.get_expense_category
                case ExtendAPITools.GET_EXPENSE_CATEGORY_LABELS.value:
                    fn = functions.get_expense_category_labels
                case ExtendAPITools.CREATE_EXPENSE_CATEGORY.value:
                    fn = functions.create_expense_category
                case ExtendAPITools.CREATE_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.create_expense_category_label
                case ExtendAPITools.UPDATE_EXPENSE_CATEGORY.value:
                    fn = functions.update_expense_category
                case ExtendAPITools.UPDATE_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.update_expense_category_label
                case ExtendAPITools.PROPOSE_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.propose_transaction_expense_data
                case ExtendAPITools.CONFIRM_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.confirm_transaction_expense_data
                case ExtendAPITools.UPDATE_TRANSACTION_EXPENSE_DATA.value:
                    fn = functions.update_transaction_expense_data
                case ExtendAPITools.CREATE_RECEIPT_ATTACHMENT.value:
                    fn = functions.create_receipt_attachment
                case ExtendAPITools.AUTOMATCH_RECEIPTS.value:
                    fn = functions.automatch_receipts
                case ExtendAPITools.GET_AUTOMATCH_STATUS.value:
                    fn = functions.get_automatch_status
                case ExtendAPITools.SEND_RECEIPT_REMINDER.value:
                    fn = functions.send_receipt_reminder
                case _:
                    raise ValueError(f"Invalid tool {tool}")

            self.add_tool(
                self._handle_tool_request(tool, fn),
                tool.name,
                tool.description
            )
            
    @classmethod
    def default_instance(cls, api_key: str, api_secret: str, configuration: Configuration):
        """Create MCP server instance for API key authentication mode."""
        return cls(
            extend_api=ExtendAPI.default_instance(api_key, api_secret), 
            configuration=configuration,
            oauth_handler=None
        )
    
    @classmethod
    def oauth_instance(cls, oauth_config: OAuthConfig, configuration: Configuration):
        """Create MCP server instance for OAuth authentication mode."""
        from .storage import create_token_store
        
        # Create token store based on OAuth configuration
        storage_config = oauth_config.get_storage_config()
        token_store = create_token_store(**storage_config)
        oauth_handler = OAuthHandler(oauth_config, token_store)
        
        return cls(
            extend_api=None,  # Will be created per-request based on user token
            configuration=configuration,
            oauth_handler=oauth_handler
        )
    
    async def authenticate_request(self, request) -> Optional[UserContext]:
        """Extract and validate Bearer token from request headers.
        
        Args:
            request: HTTP request object with headers
            
        Returns:
            UserContext if authentication successful, None otherwise
        """
        if not self.oauth_handler:
            # API key mode - no per-request authentication needed
            return None
        
        # Extract Authorization header
        auth_header = getattr(request, 'headers', {}).get('authorization', '')
        if not auth_header.startswith('Bearer '):
            logger.debug("No Bearer token found in Authorization header")
            return None
        
        # Extract token
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Validate token
        try:
            token_data = await self.oauth_handler.validate_bearer_token(token)
            if token_data:
                logger.info(f"Successfully authenticated user: {token_data.user_email}")
                return UserContext(token_data)
            else:
                logger.warning("Invalid or expired Bearer token")
                return None
        except Exception as e:
            logger.error(f"Error validating Bearer token: {e}")
            return None
    
    def set_user_context(self, user_context: Optional[UserContext]) -> None:
        """Set current user context for request processing."""
        self._current_user_context = user_context
    
    def get_current_extend_api(self) -> ExtendAPI:
        """Get ExtendAPI instance for current request context."""
        if self.oauth_handler and self._current_user_context:
            # OAuth mode - use user-specific API credentials
            return self._current_user_context.create_extend_api()
        elif self._extend:
            # API key mode - use server-wide API credentials
            return self._extend
        else:
            raise RuntimeError("No ExtendAPI available - server not properly configured")

    def _handle_tool_request(self, tool: Tool, fn: AnyFunction):
        async def resource_handler(*args, **kwargs):
            try:
                # Get appropriate ExtendAPI instance (user-specific or server-wide)
                extend_api = self.get_current_extend_api()
                
                # Execute tool with appropriate API credentials
                result = await extend_api.run(tool.method.value, *args, **kwargs)
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
            except Exception as e:
                logger.error(f"Error executing tool {tool.name}: {e}")
                
                # Return error in MCP format
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error executing tool: {str(e)}"
                        }
                    ]
                }

        orig_sig = inspect.signature(fn)
        new_params = list(orig_sig.parameters.values())[1:]
        resource_handler.__signature__ = inspect.Signature(new_params)
        return resource_handler
