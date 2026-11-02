# Endpoint contract review

This document describes the request and response behavior used by the toolkit.
Synthetic fixtures in `extend_ai_toolkit/tests/fixtures/contracts.json` cover every
catalog entry. Endpoint availability also depends on the API environment and
account permissions; a passing fixture does not establish live availability.

| Tool family | Method and path | Contract notes |
| --- | --- | --- |
| Virtual cards | GET /virtualcards and /virtualcards/{id}; PUT /virtualcards/{id}/cancel or /close | Zero-based listing; destructive writes require host approval. |
| Credit cards | GET /creditcards and /creditcards/{id} | Query `type` is singular, SOURCE or DELEGATE; both `status` and `statuses` are valid server parameters. Nullable parent/feature fields remain intact. |
| Transactions | GET /reports/transactions/v2; GET /reports/transactions/count; GET /transactions/{id} | Repeated `status`, `receiptStatus`, `expenseCategoryStatuses`; `since`/`until` for `dateType=Transaction`, `sinceClearedAt`/`untilClearedAt` for `dateType=Clear`, amount/search/card filters. One-based reports. |
| Transaction changes | PATCH /transactions/{id}/expensedata; POST /transactions/{id}/receiptreminder | Expense data is a user-facing hidden route; backend permission checks apply. An explicit null label ID clears that label and remains in host-approved arguments and the PATCH body. Reminder is an external send returning no body. |
| Expense categories/labels | GET/POST /expensedata/categories; GET/PATCH /expensedata/categories/{id}; GET/POST /expensedata/categories/{id}/labels; GET/PATCH /expensedata/categories/{id}/labels/{labelId} | Category/label names and codes have a 255-character limit. Preserve explicit false values; transaction-specific category applicability and separate card/transaction required flags are supported. |
| Organizations/users | GET /organizations; GET /organizations/{id}/members; GET /users/{id} | User-facing routes may have narrower backend authorization than API-key scope alone. Zero-based member pagination. |
| Expense policy | GET /organizations/{id}/expensepolicy | File and compilation metadata. There is no rawtext endpoint in this contract. Do not follow signed URLs automatically. |
| Receipts | POST /receiptattachments multipart; POST /receiptcapture/automatch; GET /receiptcapture/{id}/status | Upload transaction ID is optional. Tasks use PENDING/SUCCESS/FAILED/SKIPPED. |

Some report filters and user-facing routes are hidden from generated public documentation. SDK resource methods own endpoint paths and shared transaction filters. The toolkit uses those resource methods explicitly and has no silent SDK signature-based fallbacks. Extend API maintainers must review changes to those routes alongside these fixtures. Unsupported filter combinations are rejected instead of dropped.

Report `count` is a sentinel on a full page: the backend reports page × page size + 1 without proving the next page contains a row. `paginationInfo` preserves that uncertainty. A short nonempty page (or empty first page) establishes an exact count at that response snapshot. An empty later page may follow concurrent changes or an overshot page number, so it is not labeled exact.

Card create/update and recurrence validation are maintained in the SDK, including
local-date preservation, integer amount bounds, empty-note clearing and valid
month-end recurrence dates. They do not add card-creation tools to this catalog.
The app's separate final-approval route is not the ordinary card PUT operation.

Source review establishes request/response contracts, not live authorization.
These user-facing routes require user-scoped credentials, server permission and
feature checks. Enterprise service keys are not interchangeable. The app has
additional bulk, vault and approval workflows outside this toolkit's catalog.

## Gateway validation limits

Some API gateways expose fewer routes than the application API. Organization
listing, individual expense-label lookup, and receipt deletion may be unavailable
even when related read or upload operations work. Verify the routes needed by your
integration in the target environment. A 403 response can indicate route availability
or authorization; it should not be treated as an empty successful response.
