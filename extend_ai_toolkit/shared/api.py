import logging
from typing import Dict, Any, Optional

from dotenv import load_dotenv

from extend_ai_toolkit.config import API_HOST, API_VERSION
from .client import ExtendClient
from .enums import ExtendAPITools
from .functions import (
    get_virtual_card_detail,
    get_virtual_cards,
    create_virtual_card,
    close_virtual_card,
    cancel_virtual_card,
    update_virtual_card,
    get_transactions,
    get_credit_cards,
    get_transaction_detail
)
from .helpers import (
    format_virtual_cards_list,
    format_virtual_card_details,
    format_updated_virtual_card,
    format_canceled_virtual_card,
    format_closed_virtual_card,
    format_transactions_list,
    format_transaction_details,
    format_credit_cards_list
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class ExtendAPI:
    """Wrapper around Extend API"""

    def __init__(self, api_key: str, api_secret: str,
                 context: Optional[Dict[str, Any]] = None):

        extend_client = ExtendClient(
            host=API_HOST,
            version=API_VERSION,
            api_key=api_key,
            api_secret=api_secret
        )
        self.extend = extend_client
        self.context = context or {}

    async def run(self, tool: str, *args, **kwargs) -> str:
        match ExtendAPITools(tool).value:
            case ExtendAPITools.GET_VIRTUAL_CARDS.value:
                output = await get_virtual_cards(self.extend, *args, **kwargs)
                return format_virtual_cards_list(output)
            case ExtendAPITools.GET_VIRTUAL_CARD_DETAIL.value:
                output = await get_virtual_card_detail(self.extend, *args, **kwargs)
                return format_virtual_card_details(output)
            case ExtendAPITools.CREATE_VIRTUAL_CARD.value:
                output = await create_virtual_card(self.extend, *args, **kwargs)
                return format_virtual_card_details(output)
            case ExtendAPITools.UPDATE_VIRTUAL_CARD.value:
                output = await update_virtual_card(self.extend, *args, **kwargs)
                return format_updated_virtual_card(output)
            case ExtendAPITools.CANCEL_VIRTUAL_CARD.value:
                output = await cancel_virtual_card(self.extend, *args, **kwargs)
                return format_canceled_virtual_card(output)
            case ExtendAPITools.CLOSE_VIRTUAL_CARD.value:
                output = await close_virtual_card(self.extend, *args, **kwargs)
                return format_closed_virtual_card(output)
            case ExtendAPITools.GET_TRANSACTIONS.value:
                output = await get_transactions(self.extend, *args, **kwargs)
                return format_transactions_list(output)
            case ExtendAPITools.GET_TRANSACTION_DETAIL.value:
                output = await get_transaction_detail(self.extend, *args, **kwargs)
                return format_transaction_details(output)
            case ExtendAPITools.GET_CREDIT_CARDS.value:
                output = await get_credit_cards(self.extend, *args, **kwargs)
                return format_credit_cards_list(output)
            case _:
                raise ValueError(f"Invalid tool {tool}")
