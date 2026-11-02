# Tool capabilities

Generated from the shared catalog. Discovery and invocation use the same host allowlist.

| Tool | Required capabilities | Effect |
| --- | --- | --- |
| `get_virtual_cards` | virtual_cards.read | read_only |
| `get_virtual_card_detail` | virtual_cards.read | read_only |
| `cancel_virtual_card` | virtual_cards.read, virtual_cards.update | destructive |
| `close_virtual_card` | virtual_cards.read, virtual_cards.update | destructive |
| `get_credit_cards` | credit_cards.read | read_only |
| `get_credit_card_detail` | credit_cards.read | read_only |
| `get_transactions` | transactions.read | read_only |
| `count_transactions` | transactions.read | read_only |
| `get_transaction_detail` | transactions.read | read_only |
| `update_transaction_expense_data` | transactions.read, transactions.update | external_write |
| `get_expense_categories` | expense_categories.read | read_only |
| `get_expense_category` | expense_categories.read | read_only |
| `get_expense_category_labels` | expense_categories.read | read_only |
| `get_expense_category_label` | expense_categories.read | read_only |
| `create_expense_category` | expense_categories.read, expense_categories.create | external_write |
| `create_expense_category_label` | expense_categories.read, expense_categories.create | external_write |
| `update_expense_category` | expense_categories.read, expense_categories.update | external_write |
| `update_expense_category_label` | expense_categories.read, expense_categories.update | external_write |
| `get_organizations` | organizations.read | read_only |
| `get_organization_members` | organizations.read | read_only |
| `get_user_details` | users.read | read_only |
| `get_expense_policy` | expense_policies.read | read_only |
| `create_receipt_attachment` | receipt_attachments.read, receipt_attachments.create, transactions.read, transactions.update | file_upload |
| `automatch_receipts` | receipt_attachments.read, transactions.read, transactions.update | external_write |
| `get_automatch_status` | receipt_attachments.read | read_only |
| `send_receipt_reminder` | receipt_attachments.read, receipt_attachments.send, transactions.read | external_send |
