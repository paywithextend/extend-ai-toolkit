import re
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ToolArguments(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("*", mode="after")
    @classmethod
    def resource_ids(cls, value, info):
        if info.field_name.endswith("_id") and value is not None:
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", value):
                raise ValueError("Resource ID must be a single identifier")
        return value



class GetVirtualCards(ToolArguments):
    """Schema for the `get_virtual_cards` operation."""

    page: int = Field(0, description="Pagination page number, default is 0.")
    per_page: int = Field(10, description="Number of items per page, default is 10.")
    status: Optional[str] = Field(
        None,
        description="Filter virtual cards by status. Options: ACTIVE, CANCELLED, PENDING, EXPIRED, CLOSED, CONSUMED.",
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


class GetTransactions(ToolArguments):
    """Schema for the `get_transactions` operation."""

    page: int = Field(0, description="Pagination page number, default is 0.")
    per_page: int = Field(50, description="Number of transactions per page, default is 50.")
    from_date: Optional[str] = Field(
        None, description="Start date to filter transactions (YYYY-MM-DD)."
    )
    to_date: Optional[str] = Field(
        None, description="End date to filter transactions (YYYY-MM-DD)."
    )
    status: Optional[Union[List[str], str]] = Field(
        None, description="Filter transactions by status (e.g., PENDING, CLEARED, DECLINED, etc.)."
    )
    receipt_statuses: Optional[List[str]] = Field(
        None, description="Filter transactions by receipt statuses."
    )
    expense_category_statuses: Optional[List[str]] = Field(
        None,
        description="Filter transactions by expense category status, such as Attached or Missing.",
    )
    missing_expense_categories: Optional[bool] = Field(
        None, description="Filter transactions missing expense categorizations."
    )
    virtual_card_id: Optional[str] = Field(
        None, description="Filter transactions by a specific virtual card ID."
    )
    min_amount_cents: Optional[int] = Field(
        None, description="Minimum transaction amount in cents."
    )
    max_amount_cents: Optional[int] = Field(
        None, description="Maximum transaction amount in cents."
    )
    receipt_missing: Optional[bool] = Field(
        None, description="Filter transactions by whether they are missing a receipt."
    )
    search_term: Optional[str] = Field(None, description="Filter transactions by search term.")
    sort_field: Optional[str] = Field(
        None,
        description="Field to sort by, with optional direction. Use 'recipientName', 'merchantName', 'amount', 'date' for ASC. Use '-recipientName', '-merchantName', '-amount', '-date' for DESC.",
    )


class CountTransactions(ToolArguments):
    """Schema for the `count_transactions` operation."""

    from_date: Optional[str] = Field(
        None, description="Start date to filter transactions (YYYY-MM-DD)."
    )
    to_date: Optional[str] = Field(
        None, description="End date to filter transactions (YYYY-MM-DD)."
    )
    status: Optional[List[str]] = Field(
        None, description="Filter transactions by one or more statuses."
    )
    virtual_card_id: Optional[str] = Field(
        None, description="Filter transactions by a specific virtual card ID."
    )
    min_amount_cents: Optional[int] = Field(
        None, description="Minimum transaction amount in cents."
    )
    max_amount_cents: Optional[int] = Field(
        None, description="Maximum transaction amount in cents."
    )
    search_term: Optional[str] = Field(None, description="Filter transactions by search term.")
    expense_category_statuses: Optional[List[str]] = Field(
        None,
        description="Filter transactions by expense category status, such as Attached or Missing.",
    )


class GetTransactionDetail(ToolArguments):
    """Schema for the `get_transaction_detail` operation."""

    transaction_id: str = Field(
        ..., description="The ID of the transaction to retrieve details for."
    )


class UpdateTransactionExpenseData(ToolArguments):
    """Schema for the `update_transaction_expense_data` operation."""

    transaction_id: str = Field(..., description="The unique identifier of the transaction.")
    data: Dict = Field(
        ...,
        description=(
            "A dictionary representing the expense details to update. "
            "Expected format: {'expenseDetails': [{'categoryId': str, 'labelId': str}]}."
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
        ...,
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
