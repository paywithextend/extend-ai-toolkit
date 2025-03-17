import logging
from typing import Optional, Dict

import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ExtendClient:
    """Client for interacting with the Extend API"""

    def __init__(self, host: str, version: str, api_key: str, api_secret: str):
        self.host = host
        self.headers = {
            "Authorization": f"Bearer eyJraWQiOiJFTlwvVHBBOVo0d1pHMzllWlBrZWxjSDlaQVFSdU8zZVg4RUhnd2Z4cE5MQT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI4MDY0YmM5Mi00YzMxLTQ2MjctYWM2MS1mMTdkYzJkMjI0Y2EiLCJkZXZpY2Vfa2V5IjoidXMtZWFzdC0xXzliYzQ3MmU0LTVkYTEtNDA5MC05MTY3LTMwZTQzNjYxYjUwNiIsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTEuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0xX1VRd2Q3VUNKYiIsImNsaWVudF9pZCI6IjI4YnQ5ZGZva3VxcWNuNmc2OGsxMGdqcjZoIiwib3JpZ2luX2p0aSI6IjBlNmJiODUwLWMzMTktNDZjZC05ZDg4LWIxNWQ1ZWVkOThjMiIsImV2ZW50X2lkIjoiZmYxODliZTctOGM1OC00MGVlLTg3MjctNmNlNzBkZjNlMTU3IiwidG9rZW5fdXNlIjoiYWNjZXNzIiwic2NvcGUiOiJhd3MuY29nbml0by5zaWduaW4udXNlci5hZG1pbiIsImF1dGhfdGltZSI6MTc0MTk5OTYwNywiZXhwIjoxNzQyMDAwNTA3LCJpYXQiOjE3NDE5OTk2MDcsImp0aSI6IjNhODMwZTVmLWFlOGEtNGU3Ni1iYTY4LWNjYzJiMzBmNDYzMSIsInVzZXJuYW1lIjoiZmYxOGZkMzUtMTJjYi00NDlmLWEyNjUtYzUzZWQwZmVmMGMzIn0.P8SpmUzpGQ5FvyrqJTgcJXHkH968dckwH583YbICNUNT7yNgKKaYVjBiHjHsZyGxk8j2M4qf81e-GIbiOyav0davOWMUANsUnSL-TVGB6WR1ItB-R2xHjOVH-a5Q9nMXcHiMoKY3cxFNbofiZumkYzA80TEwXF4HM5P9qG4BkQJ05CdqqM9gQZEIj8l-Wz35yXnVoHQratt3gzFiE58rIJEwAowbs-XYgicPBPfhwmkU-JBZdJJVHdN7BtsPj_1iLR7a3voNFrFRHj6xTRn95RpOW07nTjlQhpP2ngwH31yJOBe4biE9Jyxy_Vffn14h-fWFYCb9dbKzQb_9HvoRWA",
            "Accept": version
        }

    async def get_virtual_cards(
            self,
            page: int = 0,
            per_page: int = 10,
            status: Optional[str] = None,
            recipient: Optional[str] = None,
            search_term: Optional[str] = None
    ) -> Dict:
        """Get list of virtual cards"""
        params = {
            "page": page,
            "perPage": per_page,
            "status": status,
            "recipient": recipient,
            "search": search_term
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{self.host}/virtualcards",
                headers=self.headers,
                params={k: v for k, v in params.items() if v is not None}
            )
            response.raise_for_status()
            return response.json()

    async def get_virtual_card_detail(self, card_id: str) -> Dict:
        """Get details of a specific virtual card"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{self.host}/virtualcards/{card_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_transactions(
            self,
            page: int = 0,
            per_page: int = 10,
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            virtual_card_id: Optional[str] = None,
            min_amount_cents: Optional[int] = None,
            max_amount_cents: Optional[int] = None
    ) -> Dict:
        """Get list of transactions"""
        params = {
            "page": page,
            "perPage": per_page,
            "since": start_date,
            "until": end_date,
            "virtualCardId": virtual_card_id,
            "minClearingBillingCents": min_amount_cents,
            "maxClearingBillingCents": max_amount_cents,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{self.host}/reports/transactions/v2",
                headers=self.headers,
                params={k: v for k, v in params.items() if v is not None}
            )
            response.raise_for_status()
            return response.json()

    async def get_transaction_detail(self, transaction_id: str) -> Dict:
        """Get details of a specific transaction"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{self.host}/transactions/{transaction_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def create_virtual_card(self, data: Dict) -> Dict:
        """Create a new virtual card"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://{self.host}/virtualcards",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def get_credit_cards(self, page: int = 0, per_page: int = 10) -> Dict:
        """Get list of credit cards"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://{self.host}/creditcards",
                headers=self.headers,
                params={"page": page, "perPage": per_page}
            )
            response.raise_for_status()
            return response.json()

    async def update_virtual_card(self, virtual_card_id: str, update_data: Dict) -> Dict:
        """Update an existing virtual card"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"https://{self.host}/virtualcards/{virtual_card_id}",
                headers=self.headers,
                json=update_data
            )
            response.raise_for_status()
            return response.json()

    async def cancel_virtual_card(self, virtual_card_id: str) -> Dict:
        """Cancel a virtual card"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"https://{self.host}/virtualcards/{virtual_card_id}/cancel",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def close_virtual_card(self, virtual_card_id: str) -> Dict:
        """Permanently close a virtual card"""
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"https://{self.host}/virtualcards/{virtual_card_id}/close",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
