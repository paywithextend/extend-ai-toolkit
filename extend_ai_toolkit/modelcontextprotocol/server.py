import inspect
import logging
from typing import Any

from mcp.server import FastMCP
from mcp.types import AnyFunction

from extend_ai_toolkit.shared import Configuration
from extend_ai_toolkit.shared import ExtendAPI
from extend_ai_toolkit.shared import ExtendAPITools
from extend_ai_toolkit.shared import functions
from extend_ai_toolkit.shared import tools, Tool
from ..__version__ import __version__ as _version

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ExtendMCPServer(FastMCP):
    def __init__(self, api_key: str, api_secret: str, configuration: Configuration):
        super().__init__(
            name="Extend MCP Server",
            version=_version
        )

        self._extend = ExtendAPI(
            api_key=api_key,
            api_secret=api_secret
        )

        for tool in configuration.allowed_tools(tools):
            fn: Any = None
            match tool.method.value:
                case ExtendAPITools.GET_VIRTUAL_CARDS.value:
                    fn = functions.get_virtual_cards
                case ExtendAPITools.GET_VIRTUAL_CARD_DETAIL.value:
                    fn = functions.get_virtual_card_detail
                case ExtendAPITools.CANCEL_VIRTUAL_CARD.value:
                    fn = functions.cancel_virtual_card
                case ExtendAPITools.CLOSE_VIRTUAL_CARD.value:
                    fn = functions.close_virtual_card
                case ExtendAPITools.GET_TRANSACTIONS.value:
                    fn = functions.get_transactions
                case ExtendAPITools.GET_TRANSACTION_DETAIL.value:
                    fn = functions.get_transaction_detail
                case ExtendAPITools.GET_CREDIT_CARDS.value:
                    fn = functions.get_credit_cards
                case ExtendAPITools.GET_CREDIT_CARD_DETAIL.value:
                    fn = functions.get_credit_card_detail
                case ExtendAPITools.GET_EXPENSE_CATEGORIES.value:
                    fn = functions.get_expense_categories
                case ExtendAPITools.GET_EXPENSE_CATEGORY.value:
                    fn = functions.get_expense_category
                case ExtendAPITools.GET_EXPENSE_CATEGORY_LABELS.value:
                    fn = functions.get_expense_category_labels
                case ExtendAPITools.CREATE_EXPENSE_CATEGORY.value:
                    fn = functions.create_expense_category
                case ExtendAPITools.CREATE_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.create_expense_category_label
                case ExtendAPITools.UPDATE_EXPENSE_CATEGORY.value:
                    fn = functions.update_expense_category
                case ExtendAPITools.UPDATE_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.update_expense_category_label
                case ExtendAPITools.PROPOSE_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.propose_transaction_expense_data
                case ExtendAPITools.CONFIRM_EXPENSE_CATEGORY_LABEL.value:
                    fn = functions.confirm_transaction_expense_data
                case ExtendAPITools.UPDATE_TRANSACTION_EXPENSE_DATA.value:
                    fn = functions.update_transaction_expense_data
                case ExtendAPITools.CREATE_RECEIPT_ATTACHMENT.value:
                    fn = functions.create_receipt_attachment
                case ExtendAPITools.AUTOMATCH_RECEIPTS.value:
                    fn = functions.automatch_receipts
                case ExtendAPITools.GET_AUTOMATCH_STATUS.value:
                    fn = functions.get_automatch_status
                case _:
                    raise ValueError(f"Invalid tool {tool}")

            self.add_tool(
                self._handle_tool_request(tool, fn),
                tool.name,
                tool.description
            )

    def _handle_tool_request(self, tool: Tool, fn: AnyFunction):
        async def resource_handler(*args, **kwargs):
            result = await self._extend.run(tool.method.value, *args, **kwargs)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }

        orig_sig = inspect.signature(fn)
        new_params = list(orig_sig.parameters.values())[1:]
        resource_handler.__signature__ = inspect.Signature(new_params)
        return resource_handler
