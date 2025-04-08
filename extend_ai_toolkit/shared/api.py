from dotenv import load_dotenv

from .enums import ExtendAPITools
from .functions import *
from .helpers import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()


class ExtendAPI:
    """Wrapper around Extend API"""

    def __init__(
            self,
            api_key: str,
            api_secret: str,
    ):

        self.extend = ExtendClient(
            api_key=api_key,
            api_secret=api_secret
        )

    async def run(self, tool: str, *args, **kwargs) -> str:
        match ExtendAPITools(tool).value:
            case ExtendAPITools.GET_VIRTUAL_CARDS.value:
                output = await get_virtual_cards(self.extend, *args, **kwargs)
                return format_virtual_cards_list(output)
            case ExtendAPITools.GET_VIRTUAL_CARD_DETAIL.value:
                output = await get_virtual_card_detail(self.extend, *args, **kwargs)
                return format_virtual_card_details(output)
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
            case ExtendAPITools.GET_CREDIT_CARD_DETAIL.value:
                output = await get_credit_card_detail(self.extend, *args, **kwargs)
                return format_credit_card_detail(output)
            case ExtendAPITools.GET_EXPENSE_CATEGORIES.value:
                output = await get_expense_categories(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.GET_EXPENSE_CATEGORY.value:
                output = await get_expense_category(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.GET_EXPENSE_CATEGORY_LABELS.value:
                output = await get_expense_category_labels(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.CREATE_EXPENSE_CATEGORY.value:
                output = await create_expense_category(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.CREATE_EXPENSE_CATEGORY_LABEL.value:
                output = await create_expense_category_label(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.UPDATE_EXPENSE_CATEGORY.value:
                output = await update_expense_category(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.UPDATE_EXPENSE_CATEGORY_LABEL.value:
                output = await update_expense_category_label(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.UPDATE_TRANSACTION_EXPENSE_DATA.value:
                output = await update_transaction_expense_data(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.PROPOSE_EXPENSE_CATEGORY_LABEL.value:
                output = await propose_transaction_expense_data(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.CONFIRM_EXPENSE_CATEGORY_LABEL.value:
                output = await confirm_transaction_expense_data(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.CREATE_RECEIPT_ATTACHMENT.value:
                output = await create_receipt_attachment(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.AUTOMATCH_RECEIPTS.value:
                output = await automatch_receipts(self.extend, *args, **kwargs)
                return json.dumps(output)
            case ExtendAPITools.GET_AUTOMATCH_STATUS.value:
                output = await get_automatch_status(self.extend, *args, **kwargs)
                return json.dumps(output)
            case _:
                raise ValueError(f"Invalid tool {tool}")
