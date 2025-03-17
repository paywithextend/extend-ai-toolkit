from enum import Enum

class ExtendAPITools(Enum):
    GET_VIRTUAL_CARDS = "get_virtual_cards"
    GET_VIRTUAL_CARD_DETAIL = "get_virtual_card_detail"
    CREATE_VIRTUAL_CARD = "create_virtual_card"
    UPDATE_VIRTUAL_CARD = "update_virtual_card"
    CANCEL_VIRTUAL_CARD = "cancel_virtual_card"
    CLOSE_VIRTUAL_CARD = "close_virtual_card"
    GET_CREDIT_CARDS = "get_credit_cards"
    GET_TRANSACTIONS = "get_transactions"
    GET_TRANSACTION_DETAIL = "get_transaction_detail"