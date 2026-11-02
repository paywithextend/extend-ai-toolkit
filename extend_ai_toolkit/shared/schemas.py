import re
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("*", mode="after")
    @classmethod
    def resource_ids(cls, value, info):
        if info.field_name.endswith("_id") and value is not None:
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", value):
                raise ValueError("Resource ID must be a single identifier")
        if info.field_name in {"name", "code"} and value is not None:
            if not value.strip() or len(value) > 255:
                raise ValueError("Name/code must be nonblank and at most 255 characters")
        if info.field_name == "page" and value is not None and value < 0:
            raise ValueError("Page must be nonnegative")
        if info.field_name in {"per_page", "count"} and value is not None and not 1 <= value <= 100:
            raise ValueError("Page size must be between 1 and 100")
        return value


class GetVirtualCards(ToolArguments):
    """Schema for the `get_virtual_cards` operation."""

    page: int = Field(0, description="Pagination page number, default is 0.")
    per_page: int = Field(10, description="Number of items per page, default is 10.")
    status: Optional[str] = Field(
        None,
        description="Filter virtual cards by status. Options: ACTIVE, CANCELLED, PENDING, EXPIRED, CLOSED, CONSUMED, REJECTED.",
    )
    recipient: Optional[str] = Field(
        None, description="Filter virtual cards by recipient identifier."
    )
    search_term: Optional[str] = Field(None, description="Search term to filter virtual cards.")
    sort_field: Optional[str] = Field(
        None,
        description="Field to sort by: 'createdAt', 'updatedAt', 'balanceCents', 'displayName', 'type', or 'status'.",
    )
    sort_direction: Optional[str] = Field(None, description="Sort direction, ASC or DESC.")


class GetVirtualCardDetail(ToolArguments):
    """Schema for the `get_virtual_card_detail` operation."""

    virtual_card_id: str = Field(..., description="The ID of the virtual card.")


class CloseVirtualCard(ToolArguments):
    """Schema for the `close_virtual_card` operation."""

    virtual_card_id: str = Field(..., description="The ID of the virtual card to close.")


class CancelVirtualCard(ToolArguments):
    """Schema for the `cancel_virtual_card` operation."""

    virtual_card_id: str = Field(..., description="The ID of the virtual card to cancel.")


class TransactionFilters(ToolArguments):
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    status: Optional[Union[List[str], str]] = None
    statuses: Optional[List[str]] = None
    receipt_statuses: Optional[List[str]] = None
    expense_category_statuses: Optional[List[str]] = None
    missing_expense_categories: Optional[bool] = None
    virtual_card_id: Optional[str] = None
    credit_card_id: Optional[str] = None
    date_type: str = Field(
        "Transaction", description="Transaction or Clear; dates filter that event."
    )
    min_amount_cents: Optional[int] = None
    max_amount_cents: Optional[int] = None
    receipt_missing: Optional[bool] = None
    search_term: Optional[str] = None
    sort_field: Optional[str] = None

    @model_validator(mode="after")
    def validate_filters(self):
        from .filters import transaction_query

        transaction_query(**self.model_dump(exclude={"page", "per_page"}))
        return self


class GetTransactions(TransactionFilters):
    """One-based transaction report pages; full-page counts are provisional."""

    page: int = Field(1, ge=1, description="One-based pagination page number, default is 1.")
    per_page: int = Field(50, ge=1, le=100)


class CountTransactions(TransactionFilters):
    """An explicit exact count with the same filters as get_transactions."""


class GetTransactionDetail(ToolArguments):
    """Schema for the `get_transaction_detail` operation."""

    transaction_id: str = Field(
        ..., description="The ID of the transaction to retrieve details for."
    )


class ExpenseDetail(ToolArguments):
    categoryId: str = Field(pattern=r"^[A-Za-z0-9_-]{1,200}$")
    labelId: Optional[str] = Field(..., pattern=r"^[A-Za-z0-9_-]{1,200}$")


class ExpenseDataUpdate(ToolArguments):
    expenseDetails: Optional[List[ExpenseDetail]] = None


class UpdateTransactionExpenseData(ToolArguments):
    """Schema for the `update_transaction_expense_data` operation."""

    transaction_id: str = Field(..., description="The unique identifier of the transaction.")
    data: ExpenseDataUpdate = Field(
        ...,
        description=(
            "A dictionary representing the expense details to update. "
            "Expected format: {'expenseDetails': [{'categoryId': str, 'labelId': str | None}]}."
        ),
    )


class GetCreditCards(ToolArguments):
    """Schema for the `get_credit_cards` operation."""

    page: int = Field(0, description="Pagination page number, default is 0.")
    per_page: int = Field(10, description="Number of credit cards per page, default is 10.")
    status: Optional[str] = Field(None, description="Filter credit cards by status.")
    type: Optional[str] = Field(
        None, description="Filter credit cards by type, such as SOURCE or DELEGATE."
    )
    search_term: Optional[str] = Field(None, description="Search term to filter credit cards.")
    sort_direction: Optional[str] = Field(None, description="Sort direction, ASC or DESC.")


class GetCreditCardDetail(ToolArguments):
    """Schema for the `get_credit_card_detail` operation."""

    credit_card_id: str = Field(
        ..., description="The ID of the credit card to retrieve details for."
    )


class GetExpenseCategories(ToolArguments):
    """Schema for the `get_expense_categories` operation."""

    active: Optional[bool] = Field(None, description="Filter categories by active status.")
    required: Optional[bool] = Field(None, description="Filter categories by required status.")
    search: Optional[str] = Field(None, description="Search term to filter categories.")
    sort_field: Optional[str] = Field(None, description="Field to sort the categories by.")
    sort_direction: Optional[str] = Field(
        None, description="Direction to sort the categories (ASC or DESC)."
    )

    transaction_id: Optional[str] = Field(
        None, description="Only fields applicable to this transaction."
    )
    required_for_transactions: Optional[bool] = None
    required_for_virtual_cards: Optional[bool] = None


class GetExpenseCategory(ToolArguments):
    """Schema for the `get_expense_category` operation."""

    category_id: str = Field(..., description="The ID of the expense category.")


class GetExpenseCategoryLabels(ToolArguments):
    """Schema for the `get_expense_category_labels` operation."""

    category_id: str = Field(..., description="The ID of the expense category.")
    page: Optional[int] = Field(0, description="Pagination page number, default is 0.")
    per_page: Optional[int] = Field(10, description="Number of labels per page, default is 10.")
    active: Optional[bool] = Field(None, description="Filter labels by active status.")
    search: Optional[str] = Field(None, description="Search term to filter labels.")
    sort_field: Optional[str] = Field(None, description="Field to sort labels by.")
    sort_direction: Optional[str] = Field(
        None, description="Direction to sort the labels (ASC or DESC)."
    )


class GetExpenseCategoryLabel(ToolArguments):
    """Schema for the `get_expense_category_label` operation."""

    category_id: str = Field(..., description="The ID of the expense category.")
    label_id: str = Field(..., description="The ID of the expense category label.")


class CreateExpenseCategory(ToolArguments):
    """Schema for the `create_expense_category` operation."""

    name: str = Field(..., description="The name of the expense category.")
    code: str = Field(..., description="A unique code for the expense category.")
    required: bool = Field(..., description="Indicates whether the expense category is required.")
    active: Optional[bool] = Field(None, description="The active status of the category.")
    free_text_allowed: Optional[bool] = Field(
        None, description="Indicates if free text is allowed."
    )

    required_for_transactions: Optional[bool] = None
    required_for_virtual_cards: Optional[bool] = None


class CreateExpenseCategoryLabel(ToolArguments):
    """Schema for the `create_expense_category_label` operation."""

    category_id: str = Field(..., description="The ID of the expense category.")
    name: str = Field(..., description="The name of the expense category label.")
    code: str = Field(..., description="A unique code for the expense category label.")
    active: bool = Field(True, description="The active status of the label (defaults to True).")


class UpdateExpenseCategory(ToolArguments):
    """Schema for the `update_expense_category` operation."""

    category_id: str = Field(..., description="The ID of the expense category to update.")
    name: Optional[str] = Field(None, description="The new name for the expense category.")
    active: Optional[bool] = Field(None, description="The updated active status.")
    required: Optional[bool] = Field(None, description="The updated required status.")
    free_text_allowed: Optional[bool] = Field(
        None, description="Indicates if free text is allowed."
    )

    required_for_transactions: Optional[bool] = None
    required_for_virtual_cards: Optional[bool] = None


class UpdateExpenseCategoryLabel(ToolArguments):
    """Schema for the `update_expense_category_label` operation."""

    category_id: str = Field(..., description="The ID of the expense category.")
    label_id: str = Field(..., description="The ID of the expense category label to update.")
    name: Optional[str] = Field(None, description="The new name for the label.")
    active: Optional[bool] = Field(None, description="The updated active status of the label.")


class GetOrganizations(ToolArguments):
    """Schema for the `get_organizations` operation."""


class GetOrganizationMembers(ToolArguments):
    """Schema for the `get_organization_members` operation."""

    organization_id: str = Field(..., description="The organization ID to retrieve members for.")
    page: Optional[int] = Field(None, description="Page number for pagination.")
    count: Optional[int] = Field(None, description="Number of members per page.")
    search: Optional[str] = Field(
        None, description="Search term to filter members by name or email."
    )
    organization_role: Optional[str] = Field(
        None, description="Filter to a single organization role."
    )
    organization_roles: Optional[List[str]] = Field(
        None, description="Filter to multiple organization roles."
    )
    show_deactivated_users: Optional[bool] = Field(
        True, description="Whether to include deactivated users."
    )
    render_metrics: Optional[bool] = Field(
        False, description="Whether to include activity metrics."
    )


class GetUserDetails(ToolArguments):
    """Schema for the `get_user_details` operation."""

    user_id: str = Field(..., description="The user ID to retrieve.")


class GetExpensePolicy(ToolArguments):
    """Schema for the `get_expense_policy` operation."""

    organization_id: str = Field(
        ..., description="The organization ID whose expense policy should be retrieved."
    )


class CreateReceiptAttachmentSchema(ToolArguments):
    """Schema for the `create_receipt_attachment` operation."""

    file_path: str = Field(
        ...,
        description="File path for the receipt attachment to be uploaded via multipart form data.",
    )
    transaction_id: Optional[str] = Field(
        None,
        description="The optional unique identifier of the transaction to attach the receipt to.",
    )


class AutomatchReceiptsSchema(ToolArguments):
    """Schema for the `automatch_receipts` operation."""

    receipt_attachment_ids: List[str] = Field(
        ..., description="A list of receipt attachment IDs to be automatched."
    )


class GetAutomatchStatusSchema(ToolArguments):
    """Schema for the `get_automatch_status` operation."""

    job_id: str = Field(
        ...,
        description="The unique identifier of the automatch job whose status is to be retrieved.",
    )


class SendReceiptReminderSchema(ToolArguments):
    """Schema for the `send_receipt_reminder` operation."""

    transaction_id: str = Field(
        ..., description="The unique identifier of the transaction to send a receipt reminder for."
    )
