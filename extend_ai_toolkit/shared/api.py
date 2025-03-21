from typing import Any

from dotenv import load_dotenv

from extend_ai_toolkit.config import API_HOST, API_VERSION
from .enums import ExtendAPITools
from .functions import *
from .helpers import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class ExtendAPI:
    """Wrapper around Extend API"""

    def __init__(self, api_key: str, api_secret: str,
                 context: Optional[Dict[str, Any]] = None):

        extend_client = ExtendClient(
            host=API_HOST if API_HOST is not None else "apiv2-stage.paywithextend.com",
            version=API_VERSION if API_VERSION is not None else "application/vnd.paywithextend.v2021-03-12+json",
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
