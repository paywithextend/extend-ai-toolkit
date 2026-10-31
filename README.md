# Extend AI Toolkit

Framework-neutral tools for Extend cards, transactions, expense data and receipts, with optional OpenAI Agents, LangChain and local MCP integrations. Version 2 requires Python 3.11+ and contains breaking security changes. Read [MIGRATION.md](MIGRATION.md) before upgrading.

## Installation

```sh
pip install extend-ai-toolkit             # lightweight core
pip install 'extend-ai-toolkit[mcp]'      # local stdio server
pip install 'extend-ai-toolkit[openai]'   # OpenAI Agents adapter
pip install 'extend-ai-toolkit[langchain]'
```

SDK `paywithextend==3.0.0` must be published before this development version can install from the registry. The dedicated CrewAI adapter and extra have been removed; applications using them need to change their integration before upgrading.

## Local MCP

Set `EXTEND_API_KEY` and `EXTEND_API_SECRET` in the host environment, then select the environment explicitly:

```sh
python -m extend_ai_toolkit.modelcontextprotocol.main --environment=stage
```

This starts a read-only local stdio server. Credentials are not accepted as command-line arguments. Unauthenticated SSE and HTTP hosting are disabled. Enabling tools in a model or adding a filesystem server does not grant write permissions.

## Core and adapters

The default catalog contains 16 read tools. The full catalog has 26 tools; discovery and invocation use the same host-owned policy. The core imports without any framework dependency.

```python
import asyncio
import os

from extend_ai_toolkit.shared import ExtendAPI

async def main():
    api = ExtendAPI.default_instance(
        api_key=os.environ['EXTEND_API_KEY'],
        api_secret=os.environ['EXTEND_API_SECRET'],
        environment='stage',
    )
    try:
        result = await api.execute('get_virtual_cards', {})
        # Handle the structured response in your application.
    finally:
        await api.aclose()

asyncio.run(main())
```

Wrap an `ExtendAPI` with `ExtendOpenAIToolkit` or `ExtendLangChainToolkit` and use `get_tools()` to register its permitted tools. LangChain execution is asynchronous. Close the shared API client when the host finishes.

## Writes and receipt files

Writes require an `ExecutionPolicy` with an explicit capability allowlist, trusted actor identity and host-owned approval callback. Approval is requested separately for each validated invocation; model booleans and confirmation tokens grant no authority. Card closure/cancellation and reminder sends have explicit effect metadata. Receipt uploads additionally require a configured directory, enforce a byte limit and file signature, reject links, and bind approval to the file snapshot hash and size.

Model calls send selected data to the chosen provider. Disable optional telemetry before importing providers with `LANGSMITH_TRACING=false` and `OTEL_SDK_DISABLED=true`. OpenAI Agent runs should use `RunConfig(tracing_disabled=True, trace_include_sensitive_data=False)`. The toolkit does not change process-wide tracing settings.

## Development and release

`make lint` and `make test` run focused checks. CI validates the base package and each optional integration on Python 3.11–3.13 and rejects active dependency advisories. API-contract and client corrections plus explicit sandbox smoke validation are required before toolkit publication; see [MIGRATION.md](MIGRATION.md).

Report security issues using [SECURITY.md](SECURITY.md). Licensed under [MIT](LICENSE).
