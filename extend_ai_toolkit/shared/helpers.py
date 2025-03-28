import json
from typing import Dict


# Helper functions for formatting responses

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


def format_updated_virtual_card(response: Dict) -> str:
    """Format the update virtual card response"""
    card = response.get("virtualCard", {})
    if not card:
        return "Virtual card not found."

    return (
        f"Virtual Card Updated Successfully!\n\n"
        f"ID: {card['id']}\n"
        f"Name: {card['displayName']}\n"
        f"Balance: ${card['balanceCents'] / 100:.2f}\n"
        f"Status: {card['status']}\n"
        f"Valid From: {card.get('validFrom', 'N/A')}\n"
        f"Valid To: {card.get('validTo', 'N/A')}\n"
        f"Notes: {card.get('notes', 'N/A')}\n"
    )


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


def format_transactions_list(response: Dict) -> str:
    """Format the transactions list response"""
    # Handle case where response is error message
    if isinstance(response, str):
        return response

    # Get report data
    report = response.get("pagination", {})
    transactions = response.get("transactions", [])
    if not transactions:
        return "No transactions found."

    # Add pagination info
    current_page = report.get("page", 1)
    total_pages = report.get("numPages", 1)
    per_page = report.get("per_page", 25)
    total_count = report.get("count", 0)

    result = f"Recent Transactions (Page {current_page} of {total_pages}, {total_count} total):\n\n"

    for txn in transactions:
        amount = txn.get('clearingBillingAmountCents', txn.get('authBillingAmountCents', 0))
        result += (
            f"- ID: {txn['id']}\n"
            f"  Merchant: {txn.get('merchantName', 'N/A')}\n"
            f"  Amount: ${amount / 100:.2f}\n"
            f"  Status: {txn['status']}\n"
            f"  Date: {txn.get('clearedAt', txn.get('authedAt', 'N/A'))}\n"
            f"  Card ID: {txn.get('virtualCardId', 'N/A')}\n"
            f"  Card Name: {txn.get('virtualCardDisplayName', 'N/A')}\n"
            f"  Card Last 4: {txn.get('last4', 'N/A')}\n"
            f"  Card Type: {txn.get('cardType', 'N/A')}\n"
            f"  Cardholder Name: {txn.get('cardholderName', 'N/A')}\n"
            f"  Recipient Name: {txn.get('recipientName', 'N/A')}\n"
            f"  Recipient Email: {txn.get('recipientEmail', 'N/A')}\n"
            f"  Auth Code: {txn.get('authCode', 'N/A')}\n"
            f"  Network: {txn.get('network', 'N/A')}\n"
            f"  Merchant Category: {txn.get('merchantCategory', 'N/A')}\n"
            f"  Merchant Category Code: {txn.get('mcc', 'N/A')}\n"
            f"  Merchant City: {txn.get('merchantCity', 'N/A')}\n"
            f"  Merchant State: {txn.get('merchantState', 'N/A')}\n"
            f"  Merchant Country: {txn.get('merchantCountry', 'N/A')}\n"
            f"  Merchant ID: {txn.get('merchantId', 'N/A')}\n"
            f"  Original Amount: ${float(txn.get('originalAmount', amount)) / 100:.2f}\n"
            f"  Currency: {txn.get('currency', 'USD')}\n"
            f"  Created At: {txn.get('createdAt', 'N/A')}\n"
            f"  Description: {txn.get('description', 'N/A')}\n"
            f"  Notes: {txn.get('notes', 'N/A')}\n"
            f"  Reference: {txn.get('reference', 'N/A')}\n\n"
        )
    if current_page < total_pages:
        result += f"\nThere are more transactions available. Use page parameter to view next page."

    return result


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
