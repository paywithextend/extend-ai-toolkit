"""Authorization code storage for OAuth 2.1 flow."""

import json
import asyncio
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta


class AuthCodeData:
    """Data structure for temporary authorization codes."""
    
    def __init__(self, code: str, user_email: str, extend_api_key: str, 
                 extend_api_secret: str, code_challenge: str, 
                 code_challenge_method: str = "S256", client_id: str = None,
                 redirect_uri: str = None, state: str = None):
        self.code = code
        self.user_email = user_email
        self.extend_api_key = extend_api_key
        self.extend_api_secret = extend_api_secret
        self.code_challenge = code_challenge
        self.code_challenge_method = code_challenge_method
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.state = state
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(minutes=10)  # Auth codes expire in 10 minutes
    
    def is_expired(self) -> bool:
        """Check if authorization code is expired."""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "code": self.code,
            "user_email": self.user_email,
            "extend_api_key": self.extend_api_key,
            "extend_api_secret": self.extend_api_secret,
            "code_challenge": self.code_challenge,
            "code_challenge_method": self.code_challenge_method,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AuthCodeData":
        """Create from dictionary."""
        auth_code = cls(
            code=data["code"],
            user_email=data["user_email"],
            extend_api_key=data["extend_api_key"],
            extend_api_secret=data["extend_api_secret"],
            code_challenge=data["code_challenge"],
            code_challenge_method=data.get("code_challenge_method", "S256"),
            client_id=data.get("client_id"),
            redirect_uri=data.get("redirect_uri"),
            state=data.get("state")
        )
        auth_code.created_at = datetime.fromisoformat(data["created_at"])
        auth_code.expires_at = datetime.fromisoformat(data["expires_at"])
        return auth_code


class AuthCodeStore:
    """Simple file-based storage for temporary authorization codes."""
    
    def __init__(self, file_path: str = "mcp_auth_codes.json"):
        """Initialize with file path."""
        self.file_path = Path(file_path)
        self._lock = asyncio.Lock()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create empty JSON file if it doesn't exist."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text("{}")
    
    async def _load_codes(self) -> Dict[str, dict]:
        """Load all authorization codes from file."""
        try:
            content = self.file_path.read_text()
            return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    async def _save_codes(self, codes: Dict[str, dict]) -> None:
        """Save all authorization codes to file."""
        self.file_path.write_text(json.dumps(codes, indent=2))
    
    async def store_auth_code(self, auth_code_data: AuthCodeData) -> None:
        """Store an authorization code."""
        async with self._lock:
            codes = await self._load_codes()
            codes[auth_code_data.code] = auth_code_data.to_dict()
            await self._save_codes(codes)
    
    async def get_auth_code(self, code: str) -> Optional[AuthCodeData]:
        """Retrieve authorization code data."""
        async with self._lock:
            codes = await self._load_codes()
            code_dict = codes.get(code)
            if code_dict:
                return AuthCodeData.from_dict(code_dict)
            return None
    
    async def delete_auth_code(self, code: str) -> bool:
        """Delete an authorization code. Returns True if code existed."""
        async with self._lock:
            codes = await self._load_codes()
            if code in codes:
                del codes[code]
                await self._save_codes(codes)
                return True
            return False
    
    async def cleanup_expired_codes(self) -> int:
        """Remove expired authorization codes. Returns count of deleted codes."""
        async with self._lock:
            codes = await self._load_codes()
            expired_codes = []
            
            for code, data in codes.items():
                auth_code_data = AuthCodeData.from_dict(data)
                if auth_code_data.is_expired():
                    expired_codes.append(code)
            
            for code in expired_codes:
                del codes[code]
            
            if expired_codes:
                await self._save_codes(codes)
            
            return len(expired_codes)