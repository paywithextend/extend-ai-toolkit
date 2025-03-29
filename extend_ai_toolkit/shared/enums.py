from enum import Enum


class ExtendAPITools(Enum):
    GET_VIRTUAL_CARDS = "get_virtual_cards"
    GET_VIRTUAL_CARD_DETAIL = "get_virtual_card_detail"
    CREATE_VIRTUAL_CARD = "create_virtual_card"
    UPDATE_VIRTUAL_CARD = "update_virtual_card"
    CANCEL_VIRTUAL_CARD = "cancel_virtual_card"
    CLOSE_VIRTUAL_CARD = "close_virtual_card"
    GET_CREDIT_CARDS = "get_credit_cards"
    GET_CREDIT_CARD_DETAIL = "get_credit_card_detail"
    GET_TRANSACTIONS = "get_transactions"
    GET_TRANSACTION_DETAIL = "get_transaction_detail"
    UPDATE_TRANSACTION_EXPENSE_DATA = "update_transaction_expense_data"
    GET_EXPENSE_CATEGORIES = "get_expense_categories"
    GET_EXPENSE_CATEGORY = "get_expense_category"
    GET_EXPENSE_CATEGORY_LABELS = "get_expense_category_labels"
    CREATE_EXPENSE_CATEGORY = "create_expense_category"
    CREATE_EXPENSE_CATEGORY_LABEL = "create_expense_category_label"
    UPDATE_EXPENSE_CATEGORY = "update_expense_category"
    UPDATE_EXPENSE_CATEGORY_LABEL = "update_expense_category_label"
    PROPOSE_EXPENSE_CATEGORY_LABEL = "propose_expense_category_label"
    CONFIRM_EXPENSE_CATEGORY_LABEL = "confirm_expense_category_label"


class Action(Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"


class Agent(Enum):
    OPENAI = "openai"
    LANGCHAIN = "langchain"


class Product(Enum):
    CREDIT_CARDS = "credit_cards"
    VIRTUAL_CARDS = "virtual_cards"
    TRANSACTIONS = "transactions"
    EXPENSE_CATEGORIES = "expense_categories"
