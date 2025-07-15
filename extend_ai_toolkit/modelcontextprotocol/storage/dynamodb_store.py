"""DynamoDB-based token storage implementation for AWS Lambda deployments."""

import os
import logging
from typing import Optional
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .base import TokenStore, TokenData

logger = logging.getLogger(__name__)


class DynamoDBTokenStore(TokenStore):
    """DynamoDB implementation of token storage for serverless deployments."""
    
    def __init__(self, table_name: str = None, region_name: str = None):
        """
        Initialize DynamoDB token store.
        
        Args:
            table_name: Name of DynamoDB table. Defaults to environment variable.
            region_name: AWS region. Defaults to environment variable.
        """
        self.table_name = table_name or os.environ.get(
            'OAUTH_TOKENS_TABLE', 
            'extend-mcp-oauth-tokens'
        )
        self.region_name = region_name or os.environ.get('AWS_REGION', 'us-east-1')
        
        try:
            # Initialize DynamoDB resource
            self.dynamodb = boto3.resource('dynamodb', region_name=self.region_name)
            self.table = self.dynamodb.Table(self.table_name)
            logger.info(f"Initialized DynamoDB token store: table={self.table_name}, region={self.region_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Ensure Lambda has proper IAM role.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB client: {e}")
            raise
    
    async def store_token(self, token_data: TokenData) -> None:
        """
        Store a token mapping in DynamoDB.
        
        Args:
            token_data: Token data to store
        """
        try:
            item = {
                'token_id': token_data.token,  # Primary key
                'user_email': token_data.user_email,
                'extend_api_key': token_data.extend_api_key,
                'extend_api_secret': token_data.extend_api_secret,
                'created_at': token_data.created_at,
                'expires_at': token_data.expires_at
            }
            
            # Remove None values to avoid DynamoDB errors
            item = {k: v for k, v in item.items() if v is not None}
            
            # Add TTL for automatic cleanup (if expires_at is provided)
            if token_data.expires_at:
                try:
                    expires_timestamp = int(datetime.fromisoformat(token_data.expires_at).timestamp())
                    item['ttl'] = expires_timestamp
                except ValueError:
                    logger.warning(f"Invalid expires_at format: {token_data.expires_at}")
            
            response = self.table.put_item(Item=item)
            logger.info(f"Stored token for user: {token_data.user_email}")
            
        except ClientError as e:
            logger.error(f"DynamoDB put_item failed: {e}")
            raise RuntimeError(f"Failed to store token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error storing token: {e}")
            raise
    
    async def get_token(self, token: str) -> Optional[TokenData]:
        """
        Retrieve token data by token from DynamoDB.
        
        Args:
            token: OAuth token to lookup
            
        Returns:
            TokenData if found, None otherwise
        """
        try:
            response = self.table.get_item(
                Key={'token_id': token}
            )
            
            if 'Item' not in response:
                logger.debug(f"Token not found: {token[:20]}...")
                return None
            
            item = response['Item']
            
            # Convert DynamoDB item back to TokenData
            token_data = TokenData(
                token=item['token_id'],
                user_email=item['user_email'],
                extend_api_key=item['extend_api_key'],
                extend_api_secret=item['extend_api_secret'],
                expires_at=item.get('expires_at')
            )
            token_data.created_at = item.get('created_at', token_data.created_at)
            
            # Check if token is expired
            if token_data.is_expired():
                logger.info(f"Token expired for user: {token_data.user_email}")
                # Optionally delete expired token immediately
                await self.delete_token(token)
                return None
            
            logger.debug(f"Retrieved token for user: {token_data.user_email}")
            return token_data
            
        except ClientError as e:
            logger.error(f"DynamoDB get_item failed: {e}")
            raise RuntimeError(f"Failed to retrieve token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving token: {e}")
            raise
    
    async def delete_token(self, token: str) -> bool:
        """
        Delete a token from DynamoDB.
        
        Args:
            token: OAuth token to delete
            
        Returns:
            True if token existed and was deleted, False otherwise
        """
        try:
            response = self.table.delete_item(
                Key={'token_id': token},
                ReturnValues='ALL_OLD'
            )
            
            deleted = 'Attributes' in response
            if deleted:
                logger.info(f"Deleted token: {token[:20]}...")
            else:
                logger.debug(f"Token not found for deletion: {token[:20]}...")
            
            return deleted
            
        except ClientError as e:
            logger.error(f"DynamoDB delete_item failed: {e}")
            raise RuntimeError(f"Failed to delete token: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting token: {e}")
            raise
    
    async def cleanup_expired_tokens(self) -> int:
        """
        Remove expired tokens from DynamoDB.
        
        Note: With TTL enabled, DynamoDB automatically deletes expired items.
        This method provides manual cleanup if needed.
        
        Returns:
            Count of deleted tokens
        """
        try:
            deleted_count = 0
            current_time = datetime.now()
            
            # Scan table for expired tokens (not efficient for large tables)
            # In production, consider using DynamoDB TTL for automatic cleanup
            response = self.table.scan()
            
            for item in response.get('Items', []):
                expires_at = item.get('expires_at')
                if expires_at:
                    try:
                        expires_datetime = datetime.fromisoformat(expires_at)
                        if expires_datetime < current_time:
                            await self.delete_token(item['token_id'])
                            deleted_count += 1
                    except ValueError:
                        # Invalid date format, delete the token
                        await self.delete_token(item['token_id'])
                        deleted_count += 1
            
            # Handle pagination if there are more items
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                for item in response.get('Items', []):
                    expires_at = item.get('expires_at')
                    if expires_at:
                        try:
                            expires_datetime = datetime.fromisoformat(expires_at)
                            if expires_datetime < current_time:
                                await self.delete_token(item['token_id'])
                                deleted_count += 1
                        except ValueError:
                            await self.delete_token(item['token_id'])
                            deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} expired tokens")
            return deleted_count
            
        except ClientError as e:
            logger.error(f"DynamoDB scan failed during cleanup: {e}")
            raise RuntimeError(f"Failed to cleanup expired tokens: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during cleanup: {e}")
            raise
    
    def health_check(self) -> bool:
        """
        Check if DynamoDB table is accessible.
        
        Returns:
            True if table is accessible, False otherwise
        """
        try:
            response = self.table.describe_table()
            table_status = response.get('Table', {}).get('TableStatus')
            is_healthy = table_status == 'ACTIVE'
            logger.debug(f"DynamoDB health check: {table_status}")
            return is_healthy
        except Exception as e:
            logger.error(f"DynamoDB health check failed: {e}")
            return False