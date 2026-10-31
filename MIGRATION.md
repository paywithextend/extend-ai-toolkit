# Version 2 migration and release prerequisites

- Requires Python 3.11+. Select `environment="stage"` or `environment="prod"` when constructing the SDK/API/toolkit, or explicitly set `ENV` to one of those values. Imports never load `.env` or choose production.
- The core default exposes 16 read tools. `Configuration.all_tools()` describes capabilities; execution still requires an `ExecutionPolicy`. Supply a host policy to `ExtendAPI`, or pass `policy=` through a toolkit factory. Missing approval hooks refuse every write. `user_confirmed_data_values` and model confirmation tokens are no longer accepted.
- `ExtendAPI.run` now returns JSON of the structured API result. Use `execute` for Python structures. Presentation formatting is opt-in.
- Close SDK clients with `async with`, `aclose()`, or toolkit `aclose()`. LangChain tools support asynchronous execution only.
- The dedicated CrewAI adapter, `extend_ai_toolkit.crewai` imports, `[crewai]` extra and agent/task/crew factories are removed in version 2. Applications using those APIs must change their integration before upgrading. The framework-neutral core and local stdio MCP remain available; the CLI exposes read tools only and is not a direct replacement for adapter write flows.
- MCP uses local stdio. The old SSE launcher exits before constructing a credential-backed server. CLI credentials come from environment variables, and the CLI is read-only. Embed the server with a trusted approval hook to enable writes.
- Configure a receipt root; upload file paths are confined to it, links are rejected, and the default maximum is 20 MiB. The approved payload includes the exact file hash and size.
- Model calls necessarily send selected data to the chosen model provider. Disable optional telemetry: OpenAI `RunConfig(tracing_disabled=True, trace_include_sensitive_data=False)`, LangSmith `LANGSMITH_TRACING=false` and OpenTelemetry `OTEL_SDK_DISABLED=true` before importing providers. Toolkit libraries do not change a host's process-wide tracing settings.

## Release order

SDK PR 29 must merge and publish `paywithextend==3.0.0` before this package can install from PyPI. Review CI temporarily builds the exact SDK commit `c092c8414a0d45a8a7aa56765e792520e20d6b31`; runtime metadata never points to Git or a local fork. This toolkit PR remains draft until the SDK release is available.

Do not publish toolkit 2.0 until the stacked API-contract/client work and sandbox smoke validation are complete. Release CI requires those contract/client test files. Publication is manual from a reviewed development tag and a previously tested wheel, through the protected `pypi` environment and Trusted Publishing. The repository owner must register the PyPI Trusted Publisher and environment protections before use; YAML alone does not perform that setup. No package has been published by this change.

`constraints/adapters.txt` records a tested Python 3.11 adapter resolution; CI also resolves each supported extra fresh on Python 3.11–3.13 and checks active PyPI advisories. All active advisories fail the audit; no dependency advisory exceptions are configured.
