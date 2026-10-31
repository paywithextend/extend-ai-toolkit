# Version 2 migration and release prerequisites

- Requires Python 3.11+. Select `environment="stage"` or `environment="prod"` when constructing the SDK/API/toolkit, or explicitly set `ENV` to one of those values. Imports never load `.env` or choose production.
- The core default exposes 16 read tools. `Configuration.all_tools()` describes capabilities; execution still requires an `ExecutionPolicy`. Supply a host policy to `ExtendAPI`, or pass `policy=` through a toolkit factory. Missing approval hooks refuse every write. `user_confirmed_data_values` and model confirmation tokens are no longer accepted.
- `ExtendAPI.run` now returns JSON of the structured API result. Use `execute` for Python structures. Presentation formatting is opt-in.
- Close SDK clients with `async with`, `aclose()`, or toolkit `aclose()`. LangChain and CrewAI tools support asynchronous execution only.
- Use separate optional-extra environments for CrewAI and OpenAI Agents/MCP 2: upstream CrewAI 1.15 requires OpenAI 2, MCP 1 and Pydantic <2.13. The toolkit MCP extra uses MCP 2 and OpenAI Agents uses OpenAI 3. Do not force incompatible extras with `--no-deps`.
- MCP uses local stdio. The old SSE launcher exits before constructing a credential-backed server. CLI credentials come from environment variables, and the CLI is read-only. Embed the server with a trusted approval hook to enable writes.
- Configure a receipt root; upload file paths are confined to it, links are rejected, and the default maximum is 20 MiB. The approved payload includes the exact file hash and size.
- Model calls necessarily send selected data to the chosen model provider. Disable optional telemetry: OpenAI `RunConfig(tracing_disabled=True, trace_include_sensitive_data=False)`, LangSmith `LANGSMITH_TRACING=false`, CrewAI `OTEL_SDK_DISABLED=true` before importing CrewAI and `tracing=False` for crews. Toolkit libraries do not change a host's process-wide tracing settings.

## Release order

SDK PR 29 must merge and publish `paywithextend==3.0.0` before this package can install from PyPI. Review CI temporarily builds the exact SDK commit `18eff6554c31841fc00f9c3a4395a76741662e90`; runtime metadata never points to Git or a local fork. This toolkit PR remains draft until the SDK release is available.

Do not publish toolkit 2.0 until the stacked API-contract/client work and sandbox smoke validation are complete. Release CI requires those contract/client test files. Publication is manual from a reviewed development tag and a previously tested wheel, through the protected `pypi` environment and Trusted Publishing. The repository owner must register the PyPI Trusted Publisher and environment protections before use; YAML alone does not perform that setup. No package has been published by this change.

`constraints/adapters.txt` records a tested Python 3.11 adapter resolution; CI also resolves each supported extra fresh on Python 3.11–3.13 and checks active PyPI advisories. CrewAI is validated separately because its upstream dependency ranges differ.

## CrewAI advisory disposition

CrewAI 1.15.33 installs ChromaDB 1.5.9. Its four underlying CVEs concern Chroma server collection APIs (remote model code loading and tenant authorization); no patched version is listed by PyPI as of 2026-10-31. This adapter starts no Chroma service, configures no model repository and creates crews with memory disabled. The exact eight advisory records and scope are recorded in `tools/advisory-dispositions.json`, owned by Extend toolkit maintainers with review due 2026-11-30. The audit reports these records explicitly and fails for new advisories, version changes or expiry. This is a bounded reachability disposition, not a claim that the CrewAI dependency graph is vulnerability-free. Applications that enable Chroma services or memory are outside that disposition.
