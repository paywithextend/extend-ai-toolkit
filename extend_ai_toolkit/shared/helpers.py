"""Optional lossless pretty-JSON presentation; API results remain structured."""
import json


def format_response(response):
    """Preserve currency codes, nullable fields and pagination precision metadata."""
    return json.dumps(response, indent=2, ensure_ascii=False, allow_nan=False)

format_virtual_cards_list = format_response
format_canceled_virtual_card = format_response
format_closed_virtual_card = format_response
format_virtual_card_details = format_response
format_credit_cards_list = format_response
format_credit_card_detail = format_response
format_transactions_list = format_response
format_transaction_details = format_response
