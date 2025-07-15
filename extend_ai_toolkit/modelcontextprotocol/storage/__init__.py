"""Token storage for OAuth 2.1 MCP implementation."""

import os
import logging
from .base import TokenStore, TokenData
from .file_store import JSONTokenStore

logger = logging.getLogger(__name__)

# Conditionally import DynamoDB store (requires boto3)
try:
    from .dynamodb_store import DynamoDBTokenStore
    DYNAMODB_AVAILABLE = True
except ImportError:
    logger.warning("boto3 not available, DynamoDB storage disabled")
    DynamoDBTokenStore = None
    DYNAMODB_AVAILABLE = False


def create_token_store(storage_type: str = None, **kwargs) -> TokenStore:
    """
    Factory function to create appropriate token store based on environment.
    
    Args:
        storage_type: "json" or "dynamodb". If None, determined from environment.
        **kwargs: Additional arguments passed to store constructor.
        
    Returns:
        TokenStore instance
        
    Raises:
        ValueError: If storage type is unsupported
        ImportError: If required dependencies are missing
    """
    # Determine storage type from environment if not specified
    if storage_type is None:
        storage_type = os.environ.get('OAUTH_STORAGE_TYPE', 'json').lower()
    
    if storage_type == 'json':
        # Default to local file storage
        file_path = kwargs.get('file_path', 'mcp_oauth_tokens.json')
        logger.info(f"Using JSON token storage: {file_path}")
        return JSONTokenStore(file_path)
    
    elif storage_type == 'dynamodb':
        if not DYNAMODB_AVAILABLE:
            raise ImportError("DynamoDB storage requires boto3. Install with: pip install boto3")
        
        table_name = kwargs.get('table_name')
        region_name = kwargs.get('region_name')
        logger.info(f"Using DynamoDB token storage: {table_name or 'default'}")
        return DynamoDBTokenStore(table_name=table_name, region_name=region_name)
    
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}. Use 'json' or 'dynamodb'")


# Export all implementations
__all__ = [
    "TokenStore", 
    "TokenData", 
    "JSONTokenStore", 
    "create_token_store"
]

if DYNAMODB_AVAILABLE:
    __all__.append("DynamoDBTokenStore")