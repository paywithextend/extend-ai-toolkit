get_virtual_cards_prompt = """
This tool will retrieve all of the user's virtual cards from Extend.
It takes the following arguments:
- page (int): The page number for the paginated list of virtual cards.
- per_page (int): The number of virtual cards per page.
- status (Optional[str]): Filter virtual cards by status (e.g., ACTIVE, CANCELLED, PENDING, EXPIRED, CLOSED, CONSUMED).
- recipient (Optional[str]): Filter by the recipient identifier.
- search_term (Optional[str]): A search term to filter the virtual cards.
- sort_field (Optional[str]): Field to sort by (e.g., 'createdAt', 'updatedAt', 'balanceCents', 'displayName', 'type', or 'status').
- sort_direction (Optional[str]): Sort direction, either ASC or DESC. USE "DESC" FOR MOST RECENT OR HIGHEST VALUES FIRST.

IMPORTANT USAGE GUIDELINES:
1. When retrieving recently created cards, ALWAYS set sort_field="createdAt" and sort_direction="DESC".
2. Use status filters whenever possible to narrow results (e.g., status="ACTIVE" for only active cards).
3. For specific cards, use search_term to reduce the result set size.

The response includes the fetched virtual cards as well pagination metadata.
"""

get_virtual_card_detail_prompt = """
This tool retrieves detailed information for a specific virtual card from Extend.
It takes the following argument:
- virtual_card_id (str): The ID of the virtual card.

The response contains all details of the virtual card.
"""

cancel_virtual_card_prompt = """
This tool cancels a virtual card in Extend.
It takes the following argument:
- virtual_card_id (str): The ID of the virtual card to cancel.
"""

close_virtual_card_prompt = """
This tool closes a virtual card in Extend.
It takes the following argument:
- virtual_card_id (str): The ID of the virtual card to close.
"""

get_credit_cards_prompt = """
This tool retrieves a list of credit cards from Extend.
It takes the following arguments:
- page (int): The page number for the paginated list.
- per_page (int): The number of credit cards per page.
- status (Optional[str]): Filter credit cards by status.
- search_term (Optional[str]): A search term to filter credit cards.
- sort_direction (Optional[str]): Sort direction (ASC or DESC).

The response includes fetched credit cards and pagination metadata.
"""

get_credit_card_detail_prompt = """
This tool retrieves detailed information for a specific credit card in Extend.
It takes the following argument:
- credit_card_id (str): The ID of the credit card.

The response includes the credit card's detailed information.
"""

get_transactions_prompt = """
This tool retrieves a list of transactions from Extend.
It takes the following arguments:
- page (int): The page number for the paginated list.
- per_page (int): The number of transactions per page.
- from_date (Optional[str]): Filter transactions starting from this date (YYYY-MM-DD).
- to_date (Optional[str]): Filter transactions up to this date (YYYY-MM-DD).
- status (Optional[str]): Filter transactions by status (e.g., PENDING, CLEARED, DECLINED, etc.).
- virtual_card_id (Optional[str]): Filter by a specific virtual card ID.
- min_amount_cents (Optional[int]): Minimum transaction amount in cents.
- max_amount_cents (Optional[int]): Maximum transaction amount in cents.
- search_term (Optional[str]): A search term to filter transactions.
- sort_field (Optional[str]): Field to sort by, with optional direction
                        Use "recipientName", "merchantName", "amount", "date" for ASC
                        Use "-recipientName", "-merchantName", "-amount", "-date" for DESC

IMPORTANT USAGE GUIDELINES:
1. When retrieving most recent transactions, ALWAYS use sort_field="-date" (negative prefix indicates descending order).
2. Use filters (from_date, to_date, status) whenever possible to reduce result set size.
3. For large result sets, use pagination appropriately with reasonable per_page values.
4. Note that sort direction is specified as part of the sort_field parameter: 
   - For DESCENDING order (newest to oldest, highest to lowest), prefix the sort_field value with "-" (e.g., "-date")
   - For ASCENDING order (oldest to newest, lowest to highest), use the sort_field value without a prefix (e.g., "date")
   There is no separate sort_direction parameter.

The response is a JSON object with a "reports" key containing:
- "transactions": An array of transaction objects
- "page": The current page number
- "pageItemCount": Number of items per page
- "totalItems": Total number of transactions matching the query
- "numberOfPages": Total number of pages available
"""

get_transaction_detail_prompt = """
This tool retrieves detailed information for a specific transaction in Extend.
It takes the following argument:
- transaction_id (str): The ID of the transaction.

The response includes the transaction's detailed information.
"""

propose_transaction_expense_data_prompt = """
IMPORTANT: This tool does NOT immediately update expense data. It only proposes changes that require user confirmation.
This tool will propose expense data changes for a specific transaction in Extend.
It takes the following arguments:
- transaction_id (str): The unique identifier of the transaction.
- data (Dict): A dictionary representing the expense data to propose.
  Expected format: {
      "expenseDetails": [{"categoryId": str, "labelId": str}]
  }

The response is a JSON object with proposal details including a confirmation token.
After calling this tool, you MUST present the confirmation details to the user and explicitly ask them to confirm before proceeding.
"""

confirm_transaction_expense_data_prompt = """
IMPORTANT: This tool finalizes expense data changes that were previously proposed.
It takes the following argument:
- confirmation_token (str): The unique token from the proposal step that was provided to the user.

DO NOT attempt to use this tool unless the user has explicitly provided the confirmation token.
The response is a JSON object with the updated transaction details.
"""

update_transaction_expense_data_prompt = """
IMPORTANT: NEVER use this tool without confirming with the user which expense category and label to use.
If the user has not specified a category and label, you must ask them for their selection before proceeding.
Only proceed with the update after receiving explicit confirmation from the user.

IMPORTANT: TRANSACTIONS of any status can be updated.

Step 1: If the user has not specified an expense category and label, present user with all of the the available categories and ask them to select one
Step 2: Once the user has confirmed the expense category, then present them with the list of labels for that expense category
Step 3: Only proceed with the update after receiving the users explicit confirmation 

This tool updates the expense data for a specific transaction in Extend.
It takes the following arguments:
- transaction_id (str): The unique identifier of the transaction.
- user_confirmed_data_values (bool): Must be True if the user has confirmed the expense category and label values.
- data (Dict): A dictionary representing the expense data to update.
  Expected format: {
      "expenseDetails": [{"categoryId": str, "labelId": str}]
  }

The response includes the updated transaction's details.
"""

get_expense_categories_prompt = """
This tool retrieves a list of expense categories from Extend.
It takes the following optional arguments:
- active (Optional[bool]): Filter categories by their active status.
- required (Optional[bool]): Filter categories by whether they are required.
- search (Optional[str]): A search term to filter categories.
- sort_field (Optional[str]): Field to sort the categories by (e.g., "name", "code", "createdAt").
- sort_direction (Optional[str]): Direction to sort ("ASC" for ascending or "DESC" for descending).

IMPORTANT USAGE GUIDELINES:
1. When retrieving categories in alphabetical order, use sort_field="name" and sort_direction="ASC".
2. When retrieving most recently created categories, use sort_field="createdAt" and sort_direction="DESC".
3. Use the active=true filter to retrieve only currently active categories.
4. When looking for a specific category, use the search parameter to narrow results.

The response includes the fetched list of expense categories.
"""

get_expense_category_prompt = """
This tool retrieves detailed information for a specific expense category from Extend.
It takes the following argument:
- category_id (str): The ID of the expense category.

The response includes the expense category details.
"""

get_expense_category_labels_prompt = """
This tool retrieves a paginated list of labels for a specific expense category in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category.
- page (Optional[int]): The page number for pagination (default is 0).
- per_page (Optional[int]): The number of labels per page (default is 10).
- active (Optional[bool]): Filter labels by their active status.
- search (Optional[str]): A search term to filter labels.
- sort_field (Optional[str]): Field to sort the labels by (e.g., "name", "code", "createdAt").
- sort_direction (Optional[str]): Direction to sort ("ASC" for ascending or "DESC" for descending).

IMPORTANT USAGE GUIDELINES:
1. The category_id parameter is required and must be valid.
2. When retrieving labels in alphabetical order, use sort_field="name" and sort_direction="ASC".
3. When retrieving most recently created labels, use sort_field="createdAt" and sort_direction="DESC".
4. Use the active=true filter to retrieve only currently active labels.
5. For retrieving all labels, increase per_page parameter to an appropriate value.
6. When looking for a specific label, use the search parameter to narrow results.

The response includes the fetched expense category labels and pagination metadata.
"""

create_expense_category_prompt = """
This tool creates a new expense category in Extend.
It takes the following arguments:
- name (str): The name of the expense category.
- code (str): A unique code for the expense category.
- required (bool): Indicates whether the expense category is required.
- active (Optional[bool]): The active status of the category.
- free_text_allowed (Optional[bool]): Indicates if free text is allowed.

The response includes the created expense category details.
"""

create_expense_category_label_prompt = """
This tool creates a new expense category label in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category.
- name (str): The name of the expense category label.
- code (str): A unique code for the expense category label.
- active (bool): The active status of the label (defaults to True).

The response includes the created expense category label details.
"""

update_expense_category_prompt = """
This tool updates an existing expense category in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category to update.
Optional arguments include:
- name (Optional[str]): The new name for the expense category.
- active (Optional[bool]): The updated active status.
- required (Optional[bool]): The updated required status.
- free_text_allowed (Optional[bool]): Indicates if free text is allowed.

The response includes the updated expense category details.
"""

update_expense_category_label_prompt = """
This tool updates an existing expense category label in Extend.
It takes the following arguments:
- category_id (str): The ID of the expense category.
- label_id (str): The ID of the expense category label to update.
Optional arguments include:
- name (Optional[str]): The new name for the label.
- active (Optional[bool]): The updated active status of the label.

The response includes the updated expense category label details.
"""

create_receipt_attachment_prompt = """
IMPORTANT: This does not require a transaction id to be passed in. Do not use one if the user does not specify a transaction id.

This tool creates a receipt attachment in Extend by uploading a file via multipart form data.
It takes the following arguments:
- file_path (str): The file path for the receipt attachment image (the file should be accessible and in a supported format, e.g., PNG, JPEG, GIF, BMP, TIFF, HEIC, or PDF).
- transaction_id (Optional[str]): The optional unique identifier of the transaction to attach the receipt to.

The response is a JSON object containing details of the receipt attachment, including:
- id: The unique identifier of the attachment.
- contentType: The MIME type (e.g., 'image/png').
- urls: A dictionary with URLs for the original image, main image, and thumbnail.
- createdAt and updatedAt timestamps.
"""

automatch_receipts_prompt = """
This tool initiates an asynchronous bulk receipt automatch job in Extend.
It takes the following argument:
- receipt_attachment_ids (List[str]): A list of receipt attachment IDs to be automatched.
The response is a JSON object containing details of the automatch job, including:
- id: The unique bulk job ID.
- tasks: A list of task objects, each including the task ID, status, associated receipt attachment ID, matched transaction ID (if available), and the count of attachments.
"""

get_automatch_status_prompt = """
This tool retrieves the status of a bulk receipt automatch job in Extend.
It takes the following argument:
- job_id (str): The unique identifier of the automatch job whose status is to be retrieved.
The response is a JSON object providing the current status and details of the job, including:
- id: The job ID.
- tasks: A list of task objects detailing each automatch operation, such as task ID, status, receipt attachment ID, matched transaction ID (if available), and attachments count.
"""
