import json
from typing import Dict


# Helper functions for formatting responses
def add_line(label, value):
    """Return a formatted line only if value is not None or 'N/A'."""
    if value is not None and value != "N/A":
        return f"  {label}: {value}\n"
    return ""

def format_virtual_cards_list(response: Dict) -> str:
    """Format the virtual cards list response"""
    pagination = response.get("pagination", {})
    cards = response.get("virtualCards", [])
    if not cards:
        return "No virtual cards found."

    result = f"Pagination:{json.dumps(pagination)}\n\nVirtual Cards:\n\n"
    for card in cards:
        result += (
            f"- ID: {card['id']}\n"
            f"  Name: {card['displayName']}\n"
            f"  Status: {card['status']}\n"
            f"  Balance: ${card['balanceCents'] / 100:.2f}\n"
            f"  Expires: {card['expires']}\n\n"
        )
    return result


def format_canceled_virtual_card(response: Dict) -> str:
    """Format the canceled virtual card response"""
    card = response.get("virtualCard", {})
    if not card:
        return "Virtual card not found."

    return (
        f"Virtual Card Cancelled Successfully!\n\n"
        f"ID: {card['id']}\n"
        f"Name: {card['displayName']}\n"
        f"Status: {card['status']}\n"
        f"Balance: ${card['balanceCents'] / 100:.2f}\n"
    )


def format_closed_virtual_card(response: Dict) -> str:
    """Format the closed virtual card response"""
    card = response.get("virtualCard", {})
    if not card:
        return "Virtual card not found."

    return (
        f"Virtual Card Closed Successfully!\n\n"
        f"ID: {card['id']}\n"
        f"Name: {card['displayName']}\n"
        f"Status: {card['status']}\n"
        f"Final Balance: ${card['balanceCents'] / 100:.2f}\n"
    )


def format_virtual_card_details(response: Dict) -> str:
    """Format the detailed virtual card response"""
    card = response.get("virtualCard", {})
    if not card:
        return "Virtual card not found."

    return (
        f"Virtual Card Details:\n\n"
        f"ID: {card['id']}\n"
        f"Name: {card['displayName']}\n"
        f"Status: {card['status']}\n"
        f"Balance: ${card['balanceCents'] / 100:.2f}\n"
        f"Spent: ${card['spentCents'] / 100:.2f}\n"
        f"Limit: ${card['limitCents'] / 100:.2f}\n"
        f"Last 4: {card['last4']}\n"
        f"Expires: {card['expires']}\n"
        f"Valid From: {card['validFrom']}\n"
        f"Valid To: {card['validTo']}\n"
        f"Recipient: {card.get('recipientId', 'N/A')}\n"
        f"Notes: {card.get('notes', 'N/A')}\n"
    )


def format_credit_cards_list(response: Dict) -> str:
    """Format the credit cards list response"""
    cards = response.get("creditCards", [])
    if not cards:
        return "No credit cards found."

    result = "Available Credit Cards:\n\n"
    for card in cards:
        result += (
            f"- ID: {card['id']}\n"
            f"  Name: {card['displayName']}\n"
            f"  Status: {card['status']}\n"
            f"  Last 4: {card['last4']}\n"
            f"  Issuer: {card['issuerName']}\n\n"
        )
    return result


def format_credit_card_detail(response: Dict) -> str:
    """Format the credit card detail response"""
    card = response.get("creditCard", {})
    if not card:
        return "No credit card found."

    card_features = card['features'] or {}
    return (
        f"Credit Card Details:\n\n"
        f"- ID: {card['id']}\n"
        f"  Name: {card['displayName']}\n"
        f"  Card User: {card['user']['firstName']} {card['user']['lastName']}\n"
        f"  Is Budget: {card['parentCreditCardId'] is not None}\n"
        f"  Status: {card['status']}\n"
        f"  Last 4: {card['last4']}\n"
        f"  Issuer: {card['issuerName']}\n"
        f"  Guest Cards Enabled: {card_features['direct']}\n"
        f"  Receipt Management Enabled: {card_features['receiptManagementEnabled']}\n"
        f"  Receipt Capture Enabled: {card_features['receiptCaptureEnabled']}\n"
        f"  Bill Pay Enabled: {card_features['billPay']}\n\n"
    )


def format_transactions_list(response: Dict) -> str:
    """Format the transactions list response"""
    # Handle case where response is error message
    if isinstance(response, str):
        return response

    # Get report data
    report = response.get("report", {})
    transactions = report.get("transactions", [])
    if not transactions:
        return "No transactions found."

    # Add pagination info
    current_page = report.get("page", 1)
    total_pages = report.get("numPages", 1)
    per_page = report.get("per_page", 25)
    total_count = report.get("count", 0)

    result = f"Recent Transactions (Page {current_page} of {total_pages}, {total_count} total):\n\n"

    for txn in transactions:
        # Always include these required fields
        txn_id = txn.get('id')
        amount_cents = txn.get('clearingBillingAmountCents', txn.get('authBillingAmountCents', 0))
        status = txn.get('status')
        
        # Start the transaction entry
        result += f"- ID: {txn_id}\n"
        result += f"  Amount: ${amount_cents / 100:.2f}\n"
        result += f"  Status: {status}\n"
        # Date can be under authedAt or clearedAt; skip if neither is provided
        txn_date = txn.get('authedAt', txn.get('clearedAt'))
        result += add_line("Date", txn_date)
        
        # Optional fields – add only if they have a valid value
        result += add_line("VCN ID", txn.get('virtualCardId'))
        result += add_line("VCN Name", txn.get('virtualCardDisplayName'))
        result += add_line("Cardholder Name", txn.get('cardholderName'))
        result += add_line("Recipient Name", txn.get('recipientName'))
        result += add_line("Merchant", txn.get('merchantName'))
        result += add_line("MCC", txn.get('mccDescription'))
        result += add_line("Notes", txn.get('notes'))
        result += add_line("Review Status", txn.get('reviewStatus'))
        result += add_line("Receipt Required", txn.get('receiptRequired'))
        result += add_line("Receipt Attachments Count", txn.get('attachmentsCount'))
        
        # For fields like connectedPlatforms that require some processing,
        # compute the value first
        synced_to_erp = True if txn.get('connectedPlatforms') and len(txn.get('connectedPlatforms')) > 0 else False
        result += add_line("Synced to ERP", synced_to_erp)
        
        # Optionally add a blank line or separator between transactions
        result += "\n"

    if current_page < total_pages:
        result += f"\nThere are more transactions available. Use page parameter to view next page."

    return result


def format_transaction_details(response: Dict) -> str:
    """Format the transaction detail response"""
    txn = response
    if not txn:
        return "Transaction not found."

    amount = txn.get('clearingBillingAmountCents', txn.get('authBillingAmountCents', 0))
    return (
        f"Transaction Details:\n\n"
        f"ID: {txn['id']}\n"
        f"Merchant: {txn.get('merchantName', 'N/A')}\n"
        f"Amount: ${amount / 100:.2f}\n"
        f"Status: {txn['status']}\n"
        f"Type: {txn['type']}\n"
        f"Card: {txn.get('virtualCardId', 'N/A')}\n"
        f"Authorization Date: {txn.get('authedAt', 'N/A')}\n"
        f"Clearing Date: {txn.get('clearedAt', 'N/A')}\n"
        f"MCC: {txn.get('mcc', 'N/A')}\n"
        f"Notes: {txn.get('notes', 'N/A')}\n"
    )
