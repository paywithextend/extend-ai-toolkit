"""JSON file-based token storage for OAuth 2.1 MCP implementation."""

import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .base import TokenStore, TokenData


class JSONTokenStore(TokenStore):
    """JSON file-based token storage implementation."""
    
    def __init__(self, file_path: str = "mcp_oauth_tokens.json"):
        """Initialize with file path."""
        self.file_path = Path(file_path)
        self._lock = asyncio.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create empty JSON file if it doesn't exist."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text("{}")
    
    async def _load_tokens(self) -> Dict[str, dict]:
        """Load all tokens from file."""
        try:
            content = self.file_path.read_text()
            return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    async def _save_tokens(self, tokens: Dict[str, dict]) -> None:
        """Save all tokens to file."""
        self.file_path.write_text(json.dumps(tokens, indent=2))
    
    async def store_token(self, token_data: TokenData) -> None:
        """Store a token mapping."""
        async with self._lock:
            tokens = await self._load_tokens()
            tokens[token_data.token] = token_data.to_dict()
            await self._save_tokens(tokens)
    
    async def get_token(self, token: str) -> Optional[TokenData]:
        """Retrieve token data by token."""
        async with self._lock:
            tokens = await self._load_tokens()
            token_dict = tokens.get(token)
            if token_dict:
                return TokenData.from_dict(token_dict)
            return None
    
    async def delete_token(self, token: str) -> bool:
        """Delete a token. Returns True if token existed."""
        async with self._lock:
            tokens = await self._load_tokens()
            if token in tokens:
                del tokens[token]
                await self._save_tokens(tokens)
                return True
            return False
    
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens. Returns count of deleted tokens."""
        async with self._lock:
            tokens = await self._load_tokens()
            expired_tokens = []
            
            for token, data in tokens.items():
                token_data = TokenData.from_dict(data)
                if token_data.is_expired():
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del tokens[token]
            
            if expired_tokens:
                await self._save_tokens(tokens)
            
            return len(expired_tokens)