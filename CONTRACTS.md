# Endpoint contract review

Reviewed 2026-10-31 against Extend development commit `a8b8c142c6cbddfb55389039ecbcf900ed362495`, refreshed before implementation. Cross-checked the corresponding request builders and response consumers in the current application source. This is source evidence, not evidence that a particular sandbox or production deployment contains that commit. Contract owner: Extend API maintainers. Synthetic request fixtures are in `extend_ai_toolkit/tests/fixtures/contracts.json` and cover every catalog entry.

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

Staging checks on 2026-10-31 returned 403 for organization listing and individual
expense-label lookup through the public API gateway. Receipt upload succeeded,
but deletion was not exposed through that gateway. An implemented application
endpoint is not sufficient evidence of public gateway exposure. These helpers
require gateway availability in addition to credentials and backend permissions;
the synthetic fixtures do not establish deployed availability.
