import io
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from extend import ExtendClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pending_selections = {}


# =========================
# Virtual Card Functions
# =========================

async def get_virtual_cards(
        extend: ExtendClient,
        page: int = 0,
        per_page: int = 10,
        status: Optional[str] = None,
        recipient: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """Get list of virtual cards

    Args:
        page (int): The page number for pagination. Defaults to 0.
        per_page (int): The number of virtual cards to return per page. Defaults to 10.
        status (Optional[str]): Filter cards by status (e.g., "ACTIVE", "CANCELLED", "PENDING", "EXPIRED", "CLOSED", "CONSUMED")
        recipient (Optional[str], optional): A filter by recipient identifier. Defaults to None.
        search_term (Optional[str], optional): A term to search virtual cards by. Defaults to None.
        sort_field (Optional[str]): Field to sort by "createdAt", "updatedAt", "balanceCents", "displayName", "type", or "status"
        sort_direction (Optional[str]): Direction to sort (ASC or DESC)
    """
    try:
        response = await extend.virtual_cards.get_virtual_cards(
            page=page,
            per_page=per_page,
            status=status.upper() if status else None,
            recipient=recipient,
            search_term=search_term,
            sort_field=sort_field,
            sort_direction=sort_direction
        )
        return response

    except Exception as e:
        logger.error("Error getting virtual cards: %s", e)
        raise Exception("Error getting virtual cards: %s", e)


async def get_virtual_card_detail(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Get details of a specific virtual card"""
    try:
        response = await extend.virtual_cards.get_virtual_card_detail(virtual_card_id)
        return response

    except Exception as e:
        logger.error("Error getting virtual card detail: %s", e)
        raise Exception(e)


async def close_virtual_card(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Close a specific virtual card"""
    try:
        response = await extend.virtual_cards.close_virtual_card(virtual_card_id)
        return response

    except Exception as e:
        logger.error("Error closing virtual card: %s", e)
        raise Exception("Error closing virtual card")


async def cancel_virtual_card(extend: ExtendClient, virtual_card_id: str) -> Dict:
    """Cancel a specific virtual card"""
    try:
        response = await extend.virtual_cards.cancel_virtual_card(virtual_card_id)
        return response

    except Exception as e:
        logger.error("Error canceling virtual card: %s", e)
        raise Exception("Error canceling virtual card")


# =========================
# Transaction Functions
# =========================

async def get_transactions(
        extend: ExtendClient,
        page: int = 0,
        per_page: int = 50,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        status: Optional[str] = None,
        virtual_card_id: Optional[str] = None,
        min_amount_cents: Optional[int] = None,
        max_amount_cents: Optional[int] = None,
        search_term: Optional[str] = None,
        sort_field: Optional[str] = None,
) -> Dict:
    """
    Get a list of recent transactions

    Args:
        page (int): pagination page number,
        per_page (int): number of transactions per page,
        from_date (Optional[str]): Start date (YYYY-MM-DD)
        to_date (Optional[str]): End date (YYYY-MM-DD)
        status (Optional[str]): Filter transactions by status (e.g., "PENDING", "CLEARED", "DECLINED", "NO_MATCH", "AVS_PASS", "AVS_FAIL", "AUTH_REVERSAL")
        virtual_card_id (Optional[str]): Filter by specific virtual card
        min_amount_cents (Optional[int]): Minimum amount in cents
        max_amount_cents (Optional[int]): Maximum amount in cents
        search_term (Optional[str]): Filter transactions by search term (e.g., "Subscription")
        sort_field (Optional[str]): Field to sort by, with optional direction
                                    Use "recipientName", "merchantName", "amount", "date" for ASC
                                    Use "-recipientName", "-merchantName", "-amount", "-date" for DESC

    """
    try:
        response = await extend.transactions.get_transactions(
            page=page,
            per_page=per_page,
            from_date=from_date,
            to_date=to_date,
            status=status.upper() if status else None,
            virtual_card_id=virtual_card_id,
            min_amount_cents=min_amount_cents,
            max_amount_cents=max_amount_cents,
            search_term=search_term,
            sort_field=sort_field
        )
        return response

    except Exception as e:
        logger.error("Error getting transactions: %s", e)
        raise Exception("Error getting transactions")


async def get_transaction_detail(extend: ExtendClient, transaction_id: str) -> Dict:
    """Get a transaction detail"""
    try:
        response = await extend.transactions.get_transaction(transaction_id)
        return response

    except Exception as e:
        logger.error("Error getting transaction detail: %s", e)
        raise Exception("Error getting transaction detail")


# =========================
# Credit Card Functions
# =========================

async def get_credit_cards(
        extend: ExtendClient,
        page: int = 0,
        per_page: int = 10,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """Get a list of credit cards"""
    try:
        response = await extend.credit_cards.get_credit_cards(
            page=page,
            per_page=per_page,
            status=status.upper() if status else None,
            search_term=search_term,
            sort_direction=sort_direction,
        )
        return response

    except Exception as e:
        logger.error("Error getting credit cards: %s", e)
        raise Exception("Error getting credit cards")


async def get_credit_card_detail(extend: ExtendClient, credit_card_id: str) -> Dict:
    """Get details of a specific credit card"""
    try:
        response = await extend.virtual_cards.get_credit_card_detail(credit_card_id)
        return response

    except Exception as e:
        logger.error("Error getting credit card details: %s", e)
        raise Exception(e)


# =========================
# Expense Data Functions
# =========================

async def get_expense_categories(
        extend: ExtendClient,
        active: Optional[bool] = None,
        required: Optional[bool] = None,
        search: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """
    Get a list of expense categories.
    """
    try:
        response = await extend.expense_data.get_expense_categories(
            active=active,
            required=required,
            search=search,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )
        return response

    except Exception as e:
        logger.error("Error getting expense categories: %s", e)
        raise Exception("Error getting expense categories: %s", e)


async def get_expense_category(extend: ExtendClient, category_id: str) -> Dict:
    """
    Get detailed information about a specific expense category.
    """
    try:
        response = await extend.expense_data.get_expense_category(category_id)
        return response

    except Exception as e:
        logger.error("Error getting expense category: %s", e)
        raise Exception("Error getting expense category: %s", e)


async def get_expense_category_labels(
        extend: ExtendClient,
        category_id: str,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
        active: Optional[bool] = None,
        search: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_direction: Optional[str] = None,
) -> Dict:
    """
    Get a paginated list of expense category labels.
    """
    try:
        response = await extend.expense_data.get_expense_category_labels(
            category_id=category_id,
            page=page,
            per_page=per_page,
            active=active,
            search=search,
            sort_field=sort_field,
            sort_direction=sort_direction,
        )
        return response

    except Exception as e:
        logger.error("Error getting expense category labels: %s", e)
        raise Exception("Error getting expense category labels: %s", e)


async def create_expense_category(
        extend: ExtendClient,
        name: str,
        code: str,
        required: bool,
        active: Optional[bool] = None,
        free_text_allowed: Optional[bool] = None,
) -> Dict:
    """
    Create an expense category.
    """
    try:
        response = await extend.expense_data.create_expense_category(
            name=name,
            code=code,
            required=required,
            active=active,
            free_text_allowed=free_text_allowed,
        )
        return response

    except Exception as e:
        logger.error("Error creating expense category: %s", e)
        raise Exception("Error creating expense category: %s", e)


async def create_expense_category_label(
        extend: ExtendClient,
        category_id: str,
        name: str,
        code: str,
        active: bool = True
) -> Dict:
    """
    Create an expense category label.
    """
    try:
        response = await extend.expense_data.create_expense_category_label(
            category_id=category_id,
            name=name,
            code=code,
            active=active
        )
        return response

    except Exception as e:
        logger.error("Error creating expense category label: %s", e)
        raise Exception("Error creating expense category label: %s", e)


async def update_expense_category(
        extend: ExtendClient,
        category_id: str,
        name: Optional[str] = None,
        active: Optional[bool] = None,
        required: Optional[bool] = None,
        free_text_allowed: Optional[bool] = None,
) -> Dict:
    """
    Update an expense category.
    """
    try:
        response = await extend.expense_data.update_expense_category(
            category_id=category_id,
            name=name,
            active=active,
            required=required,
            free_text_allowed=free_text_allowed,
        )
        return response

    except Exception as e:
        logger.error("Error updating expense category: %s", e)
        raise Exception("Error updating expense category: %s", e)


async def update_expense_category_label(
        extend: ExtendClient,
        category_id: str,
        label_id: str,
        name: Optional[str] = None,
        active: Optional[bool] = None,
) -> Dict:
    """
    Update an expense category label.
    """
    try:
        response = await extend.expense_data.update_expense_category_label(
            category_id=category_id,
            label_id=label_id,
            name=name,
            active=active,
        )
        return response

    except Exception as e:
        logger.error("Error updating expense category label: %s", e)
        raise Exception("Error updating expense category label: %s", e)


async def propose_transaction_expense_data(
        extend: ExtendClient,
        transaction_id: str,
        data: Dict
) -> Dict:
    """
    Propose expense data changes for a transaction without applying them.

    Args:
        extend: The Extend client instance
        transaction_id: The unique identifier of the transaction
        data: A dictionary representing the expense data to update

    Returns:
        Dict: A confirmation request with token and expiration
    """
    # Fetch transaction to ensure it exists
    transaction = await extend.transactions.get_transaction(transaction_id)

    # Generate a unique confirmation token
    confirmation_token = str(uuid.uuid4())

    # Set expiration time (10 minutes from now)
    expiration_time = datetime.now() + timedelta(minutes=10)

    # Store the pending selection with its metadata
    pending_selections[confirmation_token] = {
        "transaction_id": transaction_id,
        "data": data,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiration_time.isoformat(),
        "status": "pending"
    }

    # Return the confirmation request
    return {
        "status": "pending_confirmation",
        "transaction_id": transaction_id,
        "confirmation_token": confirmation_token,
        "expires_at": expiration_time.isoformat(),
        "proposed_categories": [
            {"categoryId": category.get("categoryId", "Unknown"),
             "labelId": category.get("labelId", "None")}
            for category in data.get("expenseDetails", [])
        ]
    }


async def confirm_transaction_expense_data(
        extend: ExtendClient,
        confirmation_token: str
) -> Dict:
    """
    Confirm and apply previously proposed expense data changes.

    Args:
        extend: The Extend client instance
        confirmation_token: The unique token from the proposal step

    Returns:
        Dict: The updated transaction details
    """
    # Check if token exists
    if confirmation_token not in pending_selections:
        raise Exception("Invalid confirmation token")

    # Get the pending selection
    selection = pending_selections[confirmation_token]

    # Check if expired
    if datetime.now() > datetime.fromisoformat(selection["expires_at"]):
        # Clean up expired token
        del pending_selections[confirmation_token]
        raise Exception("Confirmation token has expired")

    # Apply the expense data update
    response = await extend.transactions.update_transaction_expense_data(
        selection["transaction_id"],
        selection["data"]
    )

    # Mark as confirmed and clean up
    selection["status"] = "confirmed"
    selection["confirmed_at"] = datetime.now().isoformat()

    # In a real implementation, you might want to keep the record for auditing
    # but for simplicity, we'll delete it here
    del pending_selections[confirmation_token]

    return response


async def update_transaction_expense_data(
        extend: ExtendClient,
        transaction_id: str,
        user_confirmed_data_values: bool,
        data: Dict
) -> Dict:
    """
    Internal function to update the expense data for a specific transaction.
    This should not be exposed directly to external callers.

    Args:
        extend: The Extend client instance
        transaction_id: The unique identifier of the transaction
        user_confirmed_data_values: Only true if the user has confirmed the specific values in the data argument
        data: A dictionary representing the expense data to update

    Returns:
        Dict: A dictionary containing the updated transaction details
    """
    try:
        if not user_confirmed_data_values:
            raise Exception(f"User has not confirmed the expense category or label values")
        response = await extend.transactions.update_transaction_expense_data(transaction_id, data)
        return response
    except Exception as e:
        raise Exception(f"Error updating transaction expense data: {str(e)}")


# =========================
# Receipt Attachment Functions
# =========================

async def create_receipt_attachment(
        extend: ExtendClient,
        transaction_id: str,
        file_path: str,
) -> Dict:
    """
    Create a receipt attachment by uploading a file via multipart form data.

    Args:
        extend: The Extend client instance
        transaction_id (str): The unique identifier of the transaction to attach the receipt to.
        file_path (str): A file path for the receipt image.

    Returns:
        Dict: A dictionary representing the receipt attachment details, including:
                - id: Unique identifier of the receipt attachment.
                - transactionId: The associated transaction ID.
                - contentType: The MIME type of the uploaded file.
                - urls: A dictionary with URLs for the original image, main image, and thumbnail.
                - createdAt: Timestamp when the receipt attachment was created.
                - uploadType: A string describing the type of upload (e.g., "TRANSACTION", "VIRTUAL_CARD").
    """
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_obj = io.BytesIO(file_content)

            # Get the filename and determine the MIME type
            filename = os.path.basename(file_path)
            mime_type = None

            # Set the MIME type based on file extension
            if filename.lower().endswith('.png'):
                mime_type = 'image/png'
            elif filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
                mime_type = 'image/jpeg'
            elif filename.lower().endswith('.gif'):
                mime_type = 'image/gif'
            elif filename.lower().endswith('.bmp'):
                mime_type = 'image/bmp'
            elif filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
                mime_type = 'image/tiff'
            elif filename.lower().endswith('.heic'):
                mime_type = 'image/heic'
            elif filename.lower().endswith('.pdf'):
                mime_type = 'application/pdf'
            else:
                raise ValueError(f"Unsupported file type: {filename}")

            file_obj = io.BytesIO(file_content)
            file_obj.name = filename
            file_obj.content_type = mime_type

            response = await extend.receipt_attachments.create_receipt_attachment(
                transaction_id=transaction_id,
                file=file_obj
            )
            return response


    except Exception as e:
        logger.error("Error creating receipt attachment: %s", e)
        raise Exception("Error creating receipt attachment: %s", e)


# =========================
# Receipt Capture Functions
# =========================

async def automatch_receipts(
        extend: ExtendClient,
        receipt_attachment_ids: List[str],
) -> Dict:
    """
    Initiates an asynchronous bulk receipt automatch job.

    This method triggers an asynchronous job on the server that processes the provided receipt attachment IDs.
    The operation is non-blocking: it immediately returns a job ID and preliminary details,
    while the matching process is performed in the background.

    Args:
        receipt_attachment_ids (List[str]): A list of receipt attachment IDs to be automatched.

    Returns:
        Dict: A dictionary representing the Bulk Receipt Automatch Response.
    """
    try:
        response = await extend.receipt_capture.automatch_receipts(
            receipt_attachment_ids=receipt_attachment_ids
        )
        return response
    except Exception as e:
        logger.error("Error initiating receipt automatch: %s", e)
        raise Exception("Error initiating receipt automatch: %s", e)


async def get_automatch_status(
        extend: ExtendClient,
        job_id: str,
) -> Dict:
    """
    Retrieves the status of a bulk receipt capture automatch job.

    Args:
        job_id (str): The ID of the automatch job whose status is to be retrieved.

    Returns:
        Dict: A dictionary representing the current Bulk Receipt Automatch Response.
    """
    try:
        response = await extend.receipt_capture.get_automatch_status(job_id=job_id)
        return response
    except Exception as e:
        logger.error("Error getting automatch status: %s", e)
        raise Exception("Error getting automatch status: %s", e)


# Optional: Cleanup function to remove expired selections
async def cleanup_pending_selections():
    """Remove all expired selection tokens"""
    now = datetime.now()
    expired_tokens = [
        token for token, selection in pending_selections.items()
        if now > datetime.fromisoformat(selection["expires_at"])
    ]

    for token in expired_tokens:
        del pending_selections[token]
