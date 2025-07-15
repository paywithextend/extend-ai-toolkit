"""Base interface for token storage implementations."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime


class TokenData:
    """Data structure for OAuth token information."""
    
    def __init__(self, token: str, user_email: str, extend_api_key: str, 
                 extend_api_secret: str, expires_at: str = None):
        self.token = token
        self.user_email = user_email
        self.extend_api_key = extend_api_key
        self.extend_api_secret = extend_api_secret
        self.expires_at = expires_at
        self.created_at = datetime.now().isoformat()
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.fromisoformat(self.expires_at) < datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "token": self.token,
            "user_email": self.user_email,
            "extend_api_key": self.extend_api_key,
            "extend_api_secret": self.extend_api_secret,
            "expires_at": self.expires_at,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TokenData":
        """Create from dictionary."""
        token_data = cls(
            token=data["token"],
            user_email=data["user_email"],
            extend_api_key=data["extend_api_key"],
            extend_api_secret=data["extend_api_secret"],
            expires_at=data.get("expires_at")
        )
        token_data.created_at = data.get("created_at", token_data.created_at)
        return token_data


class TokenStore(ABC):
    """Abstract base class for token storage implementations."""
    
    @abstractmethod
    async def store_token(self, token_data: TokenData) -> None:
        """Store a token mapping."""
        pass
    
    @abstractmethod
    async def get_token(self, token: str) -> Optional[TokenData]:
        """Retrieve token data by token."""
        pass
    
    @abstractmethod
    async def delete_token(self, token: str) -> bool:
        """Delete a token. Returns True if token existed."""
        pass
    
    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        """Remove expired tokens. Returns count of deleted tokens."""
        pass