# Endpoint contract review

Reviewed 2026-10-31 against Extend development commit `a8b8c142c6cbddfb55389039ecbcf900ed362495`, refreshed before implementation. This is source evidence, not evidence that a particular sandbox or production deployment contains that commit. Contract owner: Extend API maintainers. Synthetic request fixtures are in `extend_ai_toolkit/tests/fixtures/contracts.json` and cover every catalog entry.

| Tool family | Method and path | Contract notes |
| --- | --- | --- |
| Virtual cards | GET /virtualcards and /virtualcards/{id}; PUT /virtualcards/{id}/cancel or /close | Zero-based listing; destructive writes require host approval. |
| Credit cards | GET /creditcards and /creditcards/{id} | Query `type` is singular, SOURCE or DELEGATE. Nullable parent/feature fields remain intact. |
| Transactions | GET /reports/transactions/v2; GET /reports/transactions/count; GET /transactions/{id} | Repeated `status`, `receiptStatus`, `expenseCategoryStatuses`; `since`, `until`, `dateType=Transaction`, amount/search/card filters. One-based reports. |
| Transaction changes | PATCH /transactions/{id}/expensedata; POST /transactions/{id}/receiptreminder | Expense data is a user-facing hidden route; backend permission checks apply. Reminder is an external send. |
| Expense categories/labels | GET/POST /expensedata/categories; GET/PATCH /expensedata/categories/{id}; GET/POST /expensedata/categories/{id}/labels; GET/PATCH /expensedata/categories/{id}/labels/{labelId} | Category/label names and codes have a 255-character limit. Preserve explicit false values. |
| Organizations/users | GET /organizations; GET /organizations/{id}/members; GET /users/{id} | User-facing routes may have narrower backend authorization than API-key scope alone. Zero-based member pagination. |
| Expense policy | GET /organizations/{id}/expensepolicy | File and compilation metadata. There is no rawtext endpoint in this contract. Do not follow signed URLs automatically. |
| Receipts | POST /receiptattachments multipart; POST /receiptcapture/automatch; GET /receiptcapture/{id}/status | Upload transaction ID is optional. Tasks use PENDING/SUCCESS/FAILED/SKIPPED. |

Some report filters and user-facing routes are hidden from generated public documentation. The toolkit uses the reviewed controller contract explicitly and has no silent SDK signature-based fallbacks. Extend API maintainers must review changes to those routes alongside these fixtures. Unsupported filter combinations are rejected instead of dropped.

Report `count` is a sentinel on a full page: the backend reports page × page size + 1 without proving the next page contains a row. `paginationInfo` preserves that uncertainty. A short nonempty page (or empty first page) establishes an exact count at that response snapshot. An empty later page may follow concurrent changes or an overshot page number, so it is not labeled exact.
