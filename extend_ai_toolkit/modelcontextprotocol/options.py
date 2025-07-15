import os
from typing import Optional
from ..shared.oauth_config import OAuthConfig


def validate_options(cls):
    original_init = cls.__init__

    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)

        # Perform validation after initialization
        if self.auth_mode == "api_key":
            # Validate API key mode
            if not self.api_key:
                raise ValueError(
                    'Extend API key not provided. Please either pass it as an argument --api-key=$KEY or set the EXTEND_API_KEY environment variable.'
                )
            elif not self.api_key.startswith("apik_"):
                raise ValueError('Extend API key must start with "apik_".')

            if not self.api_secret:
                raise ValueError(
                    'Extend API secret not provided. Please either pass it as an argument --api-secret=$SECRET or set the EXTEND_API_SECRET environment variable.'
                )
        
        elif self.auth_mode == "oauth":
            # Validate OAuth mode
            if not self.oauth_issuer:
                raise ValueError(
                    'OAuth issuer not provided. Please pass --oauth-issuer=https://your-server.com'
                )

        if not self.tools:
            raise ValueError('The --tools argument must be provided.')

    cls.__init__ = new_init
    return cls


@validate_options
class Options:
    ACCEPTED_ARGS = [
        'api-key', 'api-secret', 'tools',
        'oauth-mode', 'oauth-issuer', 'token-store-path', 'token-expiry-hours'
    ]

    def __init__(self, tools: str, api_key: Optional[str] = None, api_secret: Optional[str] = None,
                 oauth_mode: bool = False, oauth_issuer: Optional[str] = None,
                 token_store_path: Optional[str] = None, token_expiry_hours: int = 24):
        self.tools = tools
        
        # Determine authentication mode
        self.auth_mode = "oauth" if oauth_mode else "api_key"
        
        # API key mode fields
        self.api_key = api_key
        self.api_secret = api_secret
        
        # OAuth mode fields
        self.oauth_mode = oauth_mode
        self.oauth_issuer = oauth_issuer
        self.token_store_path = token_store_path or "mcp_oauth_tokens.json"
        self.token_expiry_hours = token_expiry_hours
    
    def get_oauth_config(self) -> Optional[OAuthConfig]:
        """Get OAuth configuration if in OAuth mode."""
        if self.auth_mode == "oauth":
            return OAuthConfig(
                issuer=self.oauth_issuer,
                token_store_path=self.token_store_path,
                token_expiry_hours=self.token_expiry_hours
            )
        return None

    @staticmethod
    def from_args(args: list[str], valid_tools: list[str]) -> "Options":
        tools = ""
        api_key = None
        api_secret = None
        oauth_mode = False
        oauth_issuer = None
        token_store_path = None
        token_expiry_hours = 24

        for arg in args:
            if arg.startswith("--"):
                arg_body = arg[2:]
                
                # Handle boolean flags (like --oauth-mode)
                if "=" not in arg_body:
                    if arg_body == "oauth-mode":
                        oauth_mode = True
                        continue
                    else:
                        raise ValueError(f"Argument {arg} is not in --key=value format.")
                
                key, value = arg_body.split("=", 1)
                match key:
                    case "tools":
                        tools = value
                    case "api-key":
                        api_key = value
                    case "api-secret":
                        api_secret = value
                    case "oauth-issuer":
                        oauth_issuer = value
                    case "token-store-path":
                        token_store_path = value
                    case "token-expiry-hours":
                        token_expiry_hours = int(value)
                    case _:
                        raise ValueError(
                            f"Invalid argument: {key}. Accepted arguments are: {', '.join(Options.ACCEPTED_ARGS)}"
                        )

        # Validate tools
        for tool in tools.split(","):
            if tool.strip() == "all":
                continue
            if tool.strip() not in valid_tools:
                raise ValueError(
                    f"Invalid tool: {tool}. Accepted tools are: {', '.join(valid_tools)}"
                )

        # Get API credentials from environment if not provided (for API key mode)
        if not oauth_mode:
            api_key = api_key or os.environ.get("EXTEND_API_KEY")
            api_secret = api_secret or os.environ.get("EXTEND_API_SECRET")

        return Options(
            tools=tools,
            api_key=api_key,
            api_secret=api_secret,
            oauth_mode=oauth_mode,
            oauth_issuer=oauth_issuer,
            token_store_path=token_store_path,
            token_expiry_hours=token_expiry_hours
        )