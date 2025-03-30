# prompts.py

get_virtual_cards_prompt = """
This tool will get all of the users virtual cards in Extend.
It takes two argument:
- page (int): the page number for the paginated list of virtual cards.
- per_page (int): the number of virtual cards per page.
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
- card_id (required): ID of the virtual card to update
- display_name (required): New or existing name for the virtual card
- balance_dollars (required): New or existing balance for the card in dollars
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
- per_page (int): the number of credit cards per page.
"""

get_credit_card_detail_prompt = """
This tool will get details of a specific credit card in Extend.
It takes one argument:
- credit_card_id (str): The ID of the credit card.
The response is a JSON object with detailed information about the credit card.
"""

get_transactions_prompt = """
This tool will get a list of transactions in Extend.
It takes two argument:
- page (int): the page number for the paginated list.
- per_page (int): the number of transactions per page.
"""

get_transaction_detail_prompt = """
This tool will get a transaction detail in Extend.
It takes one argument:
- transaction_id (str): The ID of the transaction card.
"""

propose_transaction_expense_data_prompt = """
IMPORTANT: This tool DOES NOT update the expense data yet. It only proposes changes that will need confirmation.
This tool will propose expense data changes for a transaction without applying them.
It takes the following arguments:
- transaction_id (str): The unique identifier of the transaction.
- data: A dictionary representing the expense data to propose. The shape of the data dictionary is as follows:
  {      
      "expenseDetails": [{"categoryId": str, "labelId": str}],      
  }
The response is a JSON object containing the proposal details including a confirmation token that must be used to complete the update.
After calling this tool, you MUST present the confirmation details to the user and ask them to explicitly confirm.
"""

confirm_transaction_expense_data_prompt = """
IMPORTANT: This tool finalizes expense data changes that were previously proposed.
This tool will confirm and apply expense data changes that were previously proposed.
It takes the following argument:
- confirmation_token (str): The unique token from the proposal step that was shared with the user.

The confirmation token must come directly from the user's response confirming they wish to apply the changes.
DO NOT attempt to use this tool unless the user has explicitly provided the confirmation token in their message.
The response is a JSON object containing the updated transaction details.
"""

update_transaction_expense_data_prompt = """
IMPORTANT: NEVER USE THIS TOOL WITHOUT ASKING THE USER FOR THE CATEGORY AND LABEL IF THEY HAVE NOT PROVIDED THEM.
IMPORTANT: IF THE USER DOES NOT SPECIFY WHICH CATEGORY AND LABEL TO USE, YOU ARE REQUIRED TO ASK THEM WHICH THEY WOULD LIKE TO USE.
IMPORTANT: TRANSACTIONS OF ANY STATUS CAN BE UPDATE

Step 1: Present user with the available categories and labels
Step 2: Ask you which ones you'd prefer to use
Step 3: Only proceed with the update after receiving your explicit confirmation

This tool will update the expense data for a specific transaction in Extend.
Transactions with any status can have their expense data updated.  
It takes the following arguments:
- transaction_id (str): The unique identifier of the transaction.
- user_confirmed_data_values (bool): Indicates whether or not the user has confirmed the specific values used in the data argument.
- data: A dictionary representing the expense data to update. The shape of the data dictionary is as follows:
  {      
      "expenseDetails": [{"categoryId": str, "labelId": str}],      
  }
The response is a JSON object containing the updated transaction details.
"""

# Expense Data Functions Prompts

get_expense_categories_prompt = """
This tool will get a list of expense categories in Extend.
It takes the following optional arguments:
- active (Optional[bool]): Filter categories by active status.
- required (Optional[bool]): Filter categories by required status.
- search (Optional[str]): Search term to filter categories.
- sort_field (Optional[str]): Field to sort the categories by.
- sort_direction (Optional[str]): Direction to sort (ASC or DESC).
The response is a JSON object containing a list of expense categories.
"""

get_expense_category_prompt = """
This tool will get detailed information about a specific expense category in Extend.
It takes one argument:
- category_id (str): The ID of the expense category.
The response is a JSON object with detailed information about the expense category.
"""

get_expense_category_labels_prompt = """
This tool will get a paginated list of expense category labels in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category.
- page (Optional[int]): The page number for pagination.
- per_page (Optional[int]): The number of labels per page.
- active (Optional[bool]): Filter labels by active status.
- search (Optional[str]): Search term to filter labels.
- sort_field (Optional[str]): Field to sort the labels by.
- sort_direction (Optional[str]): Direction to sort (ASC or DESC).
The response is a JSON object containing the paginated list of expense category labels.
"""

create_expense_category_prompt = """
This tool will create a new expense category in Extend.
It takes the following arguments:
- name (str): The name of the expense category.
- code (str): A unique code for the expense category.
- required (bool): Indicates whether the expense category is required.
- active (Optional[bool]): The active status of the category.
- free_text_allowed (Optional[bool]): Indicates if free text is allowed.
The response is a JSON object with the created expense category details.
"""

create_expense_category_label_prompt = """
This tool will create a new expense category label in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category.
- name (str): The name of the expense category label.
- code (str): A unique code for the expense category label.
- active (bool): The active status of the label (defaults to True).
The response is a JSON object with the created expense category label details.
"""

update_expense_category_prompt = """
This tool will update an existing expense category in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category to update.
Optional arguments include:
- name (Optional[str]): The new name for the expense category.
- active (Optional[bool]): The updated active status.
- required (Optional[bool]): The updated required status.
- free_text_allowed (Optional[bool]): Indicates if free text is allowed.
The response is a JSON object with the updated expense category details.
"""

update_expense_category_label_prompt = """
This tool will update an existing expense category label in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category.
- label_id (str): The ID of the expense category label to update.
Optional arguments include:
- name (Optional[str]): The new name for the label.
- active (Optional[bool]): The updated active status of the label.
The response is a JSON object with the updated expense category label details.
"""
