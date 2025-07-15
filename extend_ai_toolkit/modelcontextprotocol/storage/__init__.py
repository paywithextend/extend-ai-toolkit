"""Token storage for OAuth 2.1 MCP implementation."""

from .base import TokenStore, TokenData
from .file_store import JSONTokenStore

# Default implementation
TokenStore = JSONTokenStore

__all__ = ["TokenStore", "TokenData", "JSONTokenStore"]