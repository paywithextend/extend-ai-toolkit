from typing import Dict, List, TypedDict, Type

from pydantic import BaseModel

from .enums import ExtendAPITools
from .prompts import (
    get_virtual_cards_prompt,
    get_virtual_card_detail_prompt, create_virtual_card_prompt, update_virtual_card_prompt, cancel_virtual_card_prompt,
    close_virtual_card_prompt, get_transactions_prompt, get_transaction_detail_prompt, get_credit_cards_prompt,
)
from .schemas import (
    GetVirtualCards, GetVirtualCardDetail, CreateVirtualCard, UpdateVirtualCard, CancelVirtualCard, CloseVirtualCard,
    GetCreditCards, GetTransactions, GetTransactionDetail
)


class ActionDict(TypedDict):
    read: bool
    create: bool
    update: bool
    delete: bool


class Tool(BaseModel):
    method: ExtendAPITools
    name: str
    description: str
    args_schema: Type[BaseModel]
    actions: Dict[str, Dict[str, bool]]


tools: List[Tool] = [
    Tool(
        method=ExtendAPITools.GET_VIRTUAL_CARDS,
        name="Get Virtual Cards",
        description=get_virtual_cards_prompt,
        args_schema=GetVirtualCards,
        actions={
            "virtual_cards": {
                "read": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.GET_VIRTUAL_CARD_DETAIL,
        name="Get Virtual Card Detail",
        description=get_virtual_card_detail_prompt,
        args_schema=GetVirtualCardDetail,
        actions={
            "virtual_cards": {
                "read": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.CREATE_VIRTUAL_CARD,
        name="Create Virtual Card",
        description=create_virtual_card_prompt,
        args_schema=CreateVirtualCard,
        actions={
            "virtual_cards": {
                "read": True,
                "create": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.UPDATE_VIRTUAL_CARD,
        name="Update Virtual Card",
        description=update_virtual_card_prompt,
        args_schema=UpdateVirtualCard,
        actions={
            "virtual_cards": {
                "read": True,
                "update": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.CANCEL_VIRTUAL_CARD,
        name="Cancel Virtual Card",
        description=cancel_virtual_card_prompt,
        args_schema=CancelVirtualCard,
        actions={
            "virtual_cards": {
                "read": True,
                "update": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.CLOSE_VIRTUAL_CARD,
        name="Close Virtual Card",
        description=close_virtual_card_prompt,
        args_schema=CloseVirtualCard,
        actions={
            "virtual_cards": {
                "read": True,
                "update": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.GET_CREDIT_CARDS,
        name="Get Credit Cards",
        description=get_credit_cards_prompt,
        args_schema=GetCreditCards,
        actions={
            "credit_cards": {
                "read": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.GET_TRANSACTIONS,
        name="Get Transactions",
        description=get_transactions_prompt,
        args_schema=GetTransactions,
        actions={
            "transactions": {
                "read": True,
            },
        },
    ),
    Tool(
        method=ExtendAPITools.GET_TRANSACTION_DETAIL,
        name="Get Transaction Detail",
        description=get_transaction_detail_prompt,
        args_schema=GetTransactionDetail,
        actions={
            "transactions": {
                "read": True,
            },
        },
    ),
]
