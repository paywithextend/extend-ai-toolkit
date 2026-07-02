from enum import Enum


class ExtendAPITools(Enum):
    GET_VIRTUAL_CARDS = "get_virtual_cards"
    GET_VIRTUAL_CARD_DETAIL = "get_virtual_card_detail"
    CANCEL_VIRTUAL_CARD = "cancel_virtual_card"
    CLOSE_VIRTUAL_CARD = "close_virtual_card"
    GET_CREDIT_CARDS = "get_credit_cards"
    GET_CREDIT_CARD_DETAIL = "get_credit_card_detail"
    GET_TRANSACTIONS = "get_transactions"
    COUNT_TRANSACTIONS = "count_transactions"
    GET_TRANSACTION_DETAIL = "get_transaction_detail"
    UPDATE_TRANSACTION_EXPENSE_DATA = "update_transaction_expense_data"
    GET_EXPENSE_CATEGORIES = "get_expense_categories"
    GET_EXPENSE_CATEGORY = "get_expense_category"
    GET_EXPENSE_CATEGORY_LABELS = "get_expense_category_labels"
    GET_EXPENSE_CATEGORY_LABEL = "get_expense_category_label"
    CREATE_EXPENSE_CATEGORY = "create_expense_category"
    CREATE_EXPENSE_CATEGORY_LABEL = "create_expense_category_label"
    UPDATE_EXPENSE_CATEGORY = "update_expense_category"
    UPDATE_EXPENSE_CATEGORY_LABEL = "update_expense_category_label"
    TRIGGER_ASYNC_PREDICT_EXPENSE_DATA_FOR_TRANSACTIONS = (
        "trigger_async_predict_expense_data_for_transactions"
    )
    GET_ORGANIZATIONS = "get_organizations"
    GET_ORGANIZATION_MEMBERS = "get_organization_members"
    GET_USER_DETAILS = "get_user_details"
    GET_CURRENT_USER = "get_current_user"
    GET_EXPENSE_POLICY = "get_expense_policy"
    GET_SPEND_BY_EXPENSE_CATEGORY = "get_spend_by_expense_category"
    GET_SPEND_BY_MERCHANT_CATEGORY = "get_spend_by_merchant_category"
    GET_SPEND_OVER_TIME_BY_EXPENSE = "get_spend_over_time_by_expense"
    GET_SPEND_OVER_TIME_BY_MERCHANT = "get_spend_over_time_by_merchant"
    GET_SPEND_VS_PRIOR_PERIOD = "get_spend_vs_prior_period"
    PROPOSE_EXPENSE_CATEGORY_LABEL = "propose_expense_category_label"
    CONFIRM_EXPENSE_CATEGORY_LABEL = "confirm_expense_category_label"
    CREATE_RECEIPT_ATTACHMENT = "create_receipt_attachment"
    AUTOMATCH_RECEIPTS = "automatch_receipts"
    GET_AUTOMATCH_STATUS = "get_automatch_status"
    SEND_RECEIPT_REMINDER = "send_receipt_reminder"


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
    RECEIPT_ATTACHMENTS = "receipt_attachments"
    AUTOMATIONS = "automations"
    ORGANIZATIONS = "organizations"
    USERS = "users"
    EXPENSE_POLICIES = "expense_policies"
    INSIGHTS = "insights"
