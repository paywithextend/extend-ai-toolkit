from typing import List, TypedDict, Type

from pydantic import BaseModel

from .configuration import Scope, Product
from .enums import ExtendAPITools
from .prompts import (
    get_virtual_cards_prompt,
    get_virtual_card_detail_prompt,
    create_virtual_card_prompt,
    update_virtual_card_prompt,
    cancel_virtual_card_prompt,
    close_virtual_card_prompt,
    get_transactions_prompt,
    get_transaction_detail_prompt,
    get_credit_cards_prompt,
    get_expense_categories_prompt,
    get_expense_category_prompt,
    get_expense_category_labels_prompt,
    create_expense_category_prompt,
    create_expense_category_label_prompt,
    update_expense_category_prompt,
    update_expense_category_label_prompt, get_credit_card_detail_prompt,
)
from .schemas import (
    GetVirtualCards,
    GetVirtualCardDetail,
    CreateVirtualCard,
    UpdateVirtualCard,
    CancelVirtualCard,
    CloseVirtualCard,
    GetCreditCards,
    GetTransactions,
    GetTransactionDetail,
    GetExpenseCategories,
    GetExpenseCategory,
    GetExpenseCategoryLabels,
    CreateExpenseCategory,
    CreateExpenseCategoryLabel,
    UpdateExpenseCategory,
    UpdateExpenseCategoryLabel, GetCreditCardDetail,
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
    required_scope: List[Scope]


tools: List[Tool] = [
    Tool(
        method=ExtendAPITools.GET_VIRTUAL_CARDS,
        name="get_virtual_cards",
        description=get_virtual_cards_prompt,
        args_schema=GetVirtualCards,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={"read": True})
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_VIRTUAL_CARD_DETAIL,
        name="get_virtual_card_detail",
        description=get_virtual_card_detail_prompt,
        args_schema=GetVirtualCardDetail,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={"read": True})
        ],
    ),
    Tool(
        method=ExtendAPITools.CREATE_VIRTUAL_CARD,
        name="create_virtual_card",
        description=create_virtual_card_prompt,
        args_schema=CreateVirtualCard,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={
                    "read": True,
                    "create": True,
                })
        ],
    ),
    Tool(
        method=ExtendAPITools.UPDATE_VIRTUAL_CARD,
        name="update_virtual_card",
        description=update_virtual_card_prompt,
        args_schema=UpdateVirtualCard,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={
                    "read": True,
                    "update": True,
                })
        ],
    ),
    Tool(
        method=ExtendAPITools.CANCEL_VIRTUAL_CARD,
        name="cancel_virtual_card",
        description=cancel_virtual_card_prompt,
        args_schema=CancelVirtualCard,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={
                    "read": True,
                    "update": True,
                })
        ],
    ),
    Tool(
        method=ExtendAPITools.CLOSE_VIRTUAL_CARD,
        name="close_virtual_card",
        description=close_virtual_card_prompt,
        args_schema=CloseVirtualCard,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={
                    "read": True,
                    "update": True,
                })
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_CREDIT_CARDS,
        name="get_credit_cards",
        description=get_credit_cards_prompt,
        args_schema=GetCreditCards,
        required_scope=[
            Scope(
                type=Product.CREDIT_CARDS,
                actions={
                    "read": True,
                })
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_CREDIT_CARD_DETAIL,
        name="get_credit_card_detail",
        description=get_credit_card_detail_prompt,
        args_schema=GetCreditCardDetail,
        required_scope=[
            Scope(
                type=Product.CREDIT_CARDS,
                actions={"read": True}
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_TRANSACTIONS,
        name="get_transactions",
        description=get_transactions_prompt,
        args_schema=GetTransactions,
        required_scope=[
            Scope(
                type=Product.TRANSACTIONS,
                actions={
                    "read": True,
                })
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_TRANSACTION_DETAIL,
        name="get_transaction_detail",
        description=get_transaction_detail_prompt,
        args_schema=GetTransactionDetail,
        required_scope=[
            Scope(
                type=Product.TRANSACTIONS,
                actions={
                    "read": True,
                })
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_CATEGORIES,
        name="get_expense_categories",
        description=get_expense_categories_prompt,
        args_schema=GetExpenseCategories,
        required_scope=[
            Scope(
                type=Product.EXPENSE_CATEGORIES,
                actions={"read": True}
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_CATEGORY,
        name="get_expense_category",
        description=get_expense_category_prompt,
        args_schema=GetExpenseCategory,
        required_scope=[
            Scope(
                type=Product.EXPENSE_CATEGORIES,
                actions={"read": True}
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_CATEGORY_LABELS,
        name="get_expense_category_labels",
        description=get_expense_category_labels_prompt,
        args_schema=GetExpenseCategoryLabels,
        required_scope=[
            Scope(
                type=Product.EXPENSE_CATEGORIES,
                actions={"read": True}
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.CREATE_EXPENSE_CATEGORY,
        name="create_expense_category",
        description=create_expense_category_prompt,
        args_schema=CreateExpenseCategory,
        required_scope=[
            Scope(
                type=Product.EXPENSE_CATEGORIES,
                actions={"read": True, "create": True}
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.CREATE_EXPENSE_CATEGORY_LABEL,
        name="create_expense_category_label",
        description=create_expense_category_label_prompt,
        args_schema=CreateExpenseCategoryLabel,
        required_scope=[
            Scope(
                type=Product.EXPENSE_CATEGORIES,
                actions={"read": True, "create": True}
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.UPDATE_EXPENSE_CATEGORY,
        name="update_expense_category",
        description=update_expense_category_prompt,
        args_schema=UpdateExpenseCategory,
        required_scope=[
            Scope(
                type=Product.EXPENSE_CATEGORIES,
                actions={"read": True, "update": True}
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.UPDATE_EXPENSE_CATEGORY_LABEL,
        name="update_expense_category_label",
        description=update_expense_category_label_prompt,
        args_schema=UpdateExpenseCategoryLabel,
        required_scope=[
            Scope(
                type=Product.EXPENSE_CATEGORIES,
                actions={"read": True, "update": True}
            )
        ],
    ),
]
