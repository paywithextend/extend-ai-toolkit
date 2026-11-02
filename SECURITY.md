# Security

Report suspected vulnerabilities privately to support@paywithextend.com or through GitHub private vulnerability reporting when enabled. Do not post credentials, financial data, receipts or exploit details in a public issue.

Version 2 requires Python 3.11+, an explicit SDK environment, a host allowlist and a host-owned approval handler for each write. Retrieved API content and model output are untrusted. Never construct policy, actor identity or approval callbacks from tool arguments. Host approval is not replaced by a model saying that a user confirmed.

Receipt files are confined to a configured root, opened without following links, checked for format and bounded in size. Windows and platforms without safe directory-FD opening refuse uploads. Remote HTTP/SSE serving is unsupported; use local stdio.

The toolkit does not authenticate your application's users, prove their resource entitlement, or provide a human approval UI. The embedding host must authenticate its actor, choose least-privilege credentials and implement a trusted approval channel. Each callback receives an immutable canonical proposal and a unique invocation ID. Persisted approval tokens, if implemented by that host, require expiry and atomic one-use consumption outside model control.
