# prompts.py

get_virtual_cards_prompt = """
This tool will get all of the users virtual cards in Extend.
It takes two argument:
- page (int): the page number for the paginated list of virtual cards.
- page_count (int): the number of virtual cards per page.
It takes two argument:
- page (int): the page number for the paginated list of virtual cards.
- page_count (int): the number of virtual cards per page.
The response is a JSON object with two main parts:
- pagination: An object that contains metadata about the list, including the current page number, the number of virtual cards on that page, the total number of virtual cards, and the total number of pages.
- virtualCards: An array of virtual card objects.
Please note that 'totalItems' in the 'pagination' object represents the total number of virtual cards I have, even though the current page only shows a subset.
"""

get_virtual_card_detail_prompt = """
This tool will get a virtual card detail in Extend.
It takes one argument:
- virtual_card_id (str): The ID of the virtual card.
"""

create_virtual_card_prompt = """
This tool will create a virtual card in Extend.
It takes many arguments:
- credit_card_id (str): ID of the credit card to use (get this from list_credit_cards)
- display_name (str): Name for the virtual card
- amount_dollars (float): Amount to load on the card in dollars
- recipient_email (Optional[str]): Optional email address of recipient
- valid_from (Optional[str]): Optional start date (YYYY-MM-DD)
- valid_to (Optional[str]): Optional end date (YYYY-MM-DD)
- notes (Optional[str]): Optional notes for the card
- is_recurring (bool): Set to True to create a recurring card
- period (Optional[str]): DAILY, WEEKLY, MONTHLY, or YEARLY
- interval (Optional[int]): Number of periods between recurrences
- terminator (Optional[str]): NONE, COUNT, DATE, or COUNT_OR_DATE
- count (Optional[int]): Number of times to recur (for COUNT terminator)
- until (Optional[str]): End date for recurrence (for DATE terminator)
- by_week_day (Optional[int]): Day of week (0-6, Monday to Sunday) for WEEKLY recurrence
- by_month_day (Optional[int]): Day of month (1-31) for MONTHLY recurrence
- by_year_day (Optional[int]): Day of year (1-365) for YEARLY recurrence
"""

update_virtual_card_prompt = """
This tool will get update a virtual card in Extend.
It takes many arguments:
- card_id: ID of the virtual card to update
- display_name: New name for the virtual card
- balance_dollars: New balance for the card in dollars
- valid_from: New start date (YYYY-MM-DD)
- valid_to: New end date (YYYY-MM-DD)
- notes: New notes for the card
"""

cancel_virtual_card_prompt = """
This tool will get cancel virtual card in Extend.
It takes one argument:
- virtual_card_id (str): The ID of the virtual card.
"""

close_virtual_card_prompt = """
This tool will get close a virtual card in Extend.
It takes one argument:
- virtual_card_id (str): The ID of the virtual card.
"""

get_credit_cards_prompt = """
This tool will get close a virtual card in Extend.
It takes two argument:
- page (int): the page number for the paginated list.
- pageCount (int): the number of credit cards per page.
"""

get_transactions_prompt = """
This tool will get a list of transactions in Extend.
It takes two argument:
- page (int): the page number for the paginated list.
- pageCount (int): the number of transactions per page.
"""

get_transaction_detail_prompt = """
This tool will get a transaction detail in Extend.
It takes one argument:
- transaction_id (str): The ID of the transaction card.
"""
