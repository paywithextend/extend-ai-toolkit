from typing import List, Literal, Type

from pydantic import BaseModel

from .enums import ExtendAPITools, Product
from .models import Scope
from .prompts import (
    automatch_receipts_prompt,
    cancel_virtual_card_prompt,
    close_virtual_card_prompt,
    count_transactions_prompt,
    create_expense_category_label_prompt,
    create_expense_category_prompt,
    create_receipt_attachment_prompt,
    get_automatch_status_prompt,
    get_credit_card_detail_prompt,
    get_credit_cards_prompt,
    get_expense_categories_prompt,
    get_expense_category_label_prompt,
    get_expense_category_labels_prompt,
    get_expense_category_prompt,
    get_expense_policy_prompt,
    get_organization_members_prompt,
    get_organizations_prompt,
    get_transaction_detail_prompt,
    get_transactions_prompt,
    get_user_details_prompt,
    get_virtual_card_detail_prompt,
    get_virtual_cards_prompt,
    send_receipt_reminder_prompt,
    update_expense_category_label_prompt,
    update_expense_category_prompt,
    update_transaction_expense_data_prompt,
)
from .schemas import (
    AutomatchReceiptsSchema,
    CancelVirtualCard,
    CloseVirtualCard,
    CountTransactions,
    CreateExpenseCategory,
    CreateExpenseCategoryLabel,
    CreateReceiptAttachmentSchema,
    GetAutomatchStatusSchema,
    GetCreditCardDetail,
    GetCreditCards,
    GetExpenseCategories,
    GetExpenseCategory,
    GetExpenseCategoryLabel,
    GetExpenseCategoryLabels,
    GetExpensePolicy,
    GetOrganizationMembers,
    GetOrganizations,
    GetTransactionDetail,
    GetTransactions,
    GetUserDetails,
    GetVirtualCardDetail,
    GetVirtualCards,
    SendReceiptReminderSchema,
    UpdateExpenseCategory,
    UpdateExpenseCategoryLabel,
    UpdateTransactionExpenseData,
)


class Tool(BaseModel):
    side_effect_class: Literal[
        "read_only", "external_write", "destructive", "external_send", "file_upload"
    ]
    method: ExtendAPITools
    description: str
    args_schema: Type[BaseModel]
    required_scope: List[Scope]

    @property
    def name(self) -> str:
        return self.method.value


tools: List[Tool] = [
    Tool(
        method=ExtendAPITools.GET_VIRTUAL_CARDS,
        side_effect_class="read_only",
        description=get_virtual_cards_prompt,
        args_schema=GetVirtualCards,
        required_scope=[Scope(type=Product.VIRTUAL_CARDS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_VIRTUAL_CARD_DETAIL,
        side_effect_class="read_only",
        description=get_virtual_card_detail_prompt,
        args_schema=GetVirtualCardDetail,
        required_scope=[Scope(type=Product.VIRTUAL_CARDS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.CANCEL_VIRTUAL_CARD,
        side_effect_class="destructive",
        description=cancel_virtual_card_prompt,
        args_schema=CancelVirtualCard,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={
                    "read": True,
                    "update": True,
                },
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.CLOSE_VIRTUAL_CARD,
        side_effect_class="destructive",
        description=close_virtual_card_prompt,
        args_schema=CloseVirtualCard,
        required_scope=[
            Scope(
                type=Product.VIRTUAL_CARDS,
                actions={
                    "read": True,
                    "update": True,
                },
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_CREDIT_CARDS,
        side_effect_class="read_only",
        description=get_credit_cards_prompt,
        args_schema=GetCreditCards,
        required_scope=[
            Scope(
                type=Product.CREDIT_CARDS,
                actions={
                    "read": True,
                },
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_CREDIT_CARD_DETAIL,
        side_effect_class="read_only",
        description=get_credit_card_detail_prompt,
        args_schema=GetCreditCardDetail,
        required_scope=[Scope(type=Product.CREDIT_CARDS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_TRANSACTIONS,
        side_effect_class="read_only",
        description=get_transactions_prompt,
        args_schema=GetTransactions,
        required_scope=[
            Scope(
                type=Product.TRANSACTIONS,
                actions={
                    "read": True,
                },
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.COUNT_TRANSACTIONS,
        side_effect_class="read_only",
        description=count_transactions_prompt,
        args_schema=CountTransactions,
        required_scope=[Scope(type=Product.TRANSACTIONS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_TRANSACTION_DETAIL,
        side_effect_class="read_only",
        description=get_transaction_detail_prompt,
        args_schema=GetTransactionDetail,
        required_scope=[
            Scope(
                type=Product.TRANSACTIONS,
                actions={
                    "read": True,
                },
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.UPDATE_TRANSACTION_EXPENSE_DATA,
        side_effect_class="external_write",
        description=update_transaction_expense_data_prompt,
        args_schema=UpdateTransactionExpenseData,
        required_scope=[
            Scope(
                type=Product.TRANSACTIONS,
                actions={
                    "read": True,
                    "update": True,
                },
            )
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_CATEGORIES,
        side_effect_class="read_only",
        description=get_expense_categories_prompt,
        args_schema=GetExpenseCategories,
        required_scope=[Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_CATEGORY,
        side_effect_class="read_only",
        description=get_expense_category_prompt,
        args_schema=GetExpenseCategory,
        required_scope=[Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_CATEGORY_LABELS,
        side_effect_class="read_only",
        description=get_expense_category_labels_prompt,
        args_schema=GetExpenseCategoryLabels,
        required_scope=[Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_CATEGORY_LABEL,
        side_effect_class="read_only",
        description=get_expense_category_label_prompt,
        args_schema=GetExpenseCategoryLabel,
        required_scope=[Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.CREATE_EXPENSE_CATEGORY,
        side_effect_class="external_write",
        description=create_expense_category_prompt,
        args_schema=CreateExpenseCategory,
        required_scope=[
            Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True, "create": True})
        ],
    ),
    Tool(
        method=ExtendAPITools.CREATE_EXPENSE_CATEGORY_LABEL,
        side_effect_class="external_write",
        description=create_expense_category_label_prompt,
        args_schema=CreateExpenseCategoryLabel,
        required_scope=[
            Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True, "create": True})
        ],
    ),
    Tool(
        method=ExtendAPITools.UPDATE_EXPENSE_CATEGORY,
        side_effect_class="external_write",
        description=update_expense_category_prompt,
        args_schema=UpdateExpenseCategory,
        required_scope=[
            Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True, "update": True})
        ],
    ),
    Tool(
        method=ExtendAPITools.UPDATE_EXPENSE_CATEGORY_LABEL,
        side_effect_class="external_write",
        description=update_expense_category_label_prompt,
        args_schema=UpdateExpenseCategoryLabel,
        required_scope=[
            Scope(type=Product.EXPENSE_CATEGORIES, actions={"read": True, "update": True})
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_ORGANIZATIONS,
        side_effect_class="read_only",
        description=get_organizations_prompt,
        args_schema=GetOrganizations,
        required_scope=[Scope(type=Product.ORGANIZATIONS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_ORGANIZATION_MEMBERS,
        side_effect_class="read_only",
        description=get_organization_members_prompt,
        args_schema=GetOrganizationMembers,
        required_scope=[Scope(type=Product.ORGANIZATIONS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_USER_DETAILS,
        side_effect_class="read_only",
        description=get_user_details_prompt,
        args_schema=GetUserDetails,
        required_scope=[Scope(type=Product.USERS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.GET_EXPENSE_POLICY,
        side_effect_class="read_only",
        description=get_expense_policy_prompt,
        args_schema=GetExpensePolicy,
        required_scope=[Scope(type=Product.EXPENSE_POLICIES, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.CREATE_RECEIPT_ATTACHMENT,
        side_effect_class="file_upload",
        description=create_receipt_attachment_prompt,
        args_schema=CreateReceiptAttachmentSchema,
        required_scope=[
            Scope(type=Product.RECEIPT_ATTACHMENTS, actions={"read": True, "create": True}),
            Scope(type=Product.TRANSACTIONS, actions={"read": True, "update": True}),
        ],
    ),
    Tool(
        method=ExtendAPITools.AUTOMATCH_RECEIPTS,
        side_effect_class="external_write",
        description=automatch_receipts_prompt,
        args_schema=AutomatchReceiptsSchema,
        required_scope=[
            Scope(type=Product.RECEIPT_ATTACHMENTS, actions={"read": True}),
            Scope(type=Product.TRANSACTIONS, actions={"read": True, "update": True}),
        ],
    ),
    Tool(
        method=ExtendAPITools.GET_AUTOMATCH_STATUS,
        side_effect_class="read_only",
        description=get_automatch_status_prompt,
        args_schema=GetAutomatchStatusSchema,
        required_scope=[Scope(type=Product.RECEIPT_ATTACHMENTS, actions={"read": True})],
    ),
    Tool(
        method=ExtendAPITools.SEND_RECEIPT_REMINDER,
        side_effect_class="external_send",
        description=send_receipt_reminder_prompt,
        args_schema=SendReceiptReminderSchema,
        required_scope=[
            Scope(type=Product.RECEIPT_ATTACHMENTS, actions={"read": True, "send": True}),
            Scope(type=Product.TRANSACTIONS, actions={"read": True}),
        ],
    ),
]
