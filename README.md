# Extend AI Toolkit

Framework-neutral tools for Extend cards, transactions, expense data and receipts, with adapters for OpenAI Agents, LangChain and local MCP. Requires Python 3.11+. Version 2 is a breaking development release; see [migration and release prerequisites](MIGRATION.md).

## Install

```sh
pip install extend-ai-toolkit                 # core only
pip install 'extend-ai-toolkit[mcp]'          # local stdio server
pip install 'extend-ai-toolkit[openai]'       # OpenAI Agents
pip install 'extend-ai-toolkit[langchain]'    # langchain-core tools
```

SDK 3.0.0 must be published before version 2 can install from the registry. The dedicated CrewAI adapter, extra and agent/task/crew factories are removed in version 2. See [MIGRATION.md](MIGRATION.md) before upgrading an application that uses them.

## Local MCP

Set `EXTEND_API_KEY` and `EXTEND_API_SECRET` in the host's secret environment and choose the environment explicitly:

```sh
python -m extend_ai_toolkit.modelcontextprotocol.main --environment=stage
```

The CLI exposes 16 read tools over local stdio. Credentials are not accepted as command-line arguments. Embed `ExtendMCPServer` with a trusted host policy to permit writes. Unauthenticated SSE and HTTP hosting are disabled. Adding a filesystem server does not grant receipt-upload authority.

## Core reads

```python
import os
from extend import ExtendClient
from extend.auth import BasicAuth
from extend_ai_toolkit import execute_tool

async def recent_transactions():
    async with ExtendClient(
        auth=BasicAuth(os.environ["EXTEND_API_KEY"], os.environ["EXTEND_API_SECRET"]),
        environment="stage",  # select prod explicitly when appropriate
    ) as client:
        return await execute_tool(client, "get_transactions", {
            "page": 1, "per_page": 25,
            "statuses": ["CLEARED", "PENDING"],
            "receipt_statuses": ["Missing"],
        })
```

Imports do not load `.env` or choose an environment. Return values retain original JSON structures, currency codes and optional fields. `ExtendAPI.execute` returns structures; adapter `run` outputs serialize them as JSON. The optional `shared.helpers.format_response` pretty-prints the complete response.

Transaction pages start at **1**; card, category-label and member pages start at **0**. Full transaction pages carry provisional backend counts; `paginationInfo.countExact` is false and `mayHaveMore` is true. Follow `nextPage` with a bounded loop; an empty page can end a full-page sequence. Use `count_transactions` only when an exact total is needed. The list and count tools share filters. Unsupported status values, conflicting aliases, invalid dates and inverted ranges fail before HTTP.

The expense-policy tool returns file and compilation metadata, not raw policy text. It never follows the signed URLs in that response. Treat those URLs, notes, merchant descriptions and other fetched content as sensitive, untrusted data.

## Host-controlled writes

The default policy exposes 16 reads. [CAPABILITIES.md](CAPABILITIES.md) lists all 26 tools, scopes and effects. Configuration is host-owned; it cannot grant authority through model arguments. `all` enables discovery only when used to construct an explicit policy; it never substitutes for approval.

```python
from pathlib import Path
from extend_ai_toolkit import ExecutionPolicy
from extend_ai_toolkit.shared import Configuration, ExtendAPI

async def approved_api(client, authenticated_user_id, approval_service):
    async def approve(request):
        # This service is trusted host/UI code, outside the model and tool schemas.
        # Display request.tool_name and request.arguments_json to the authenticated
        # actor and return True only for this invocation_id and payload_sha256.
        return await approval_service.request_decision(request)

    policy = ExecutionPolicy.from_configuration(
        Configuration.from_tool_str(
            "transactions.read,transactions.update,"
            "receipt_attachments.read,receipt_attachments.create"
        ),
        actor_id=authenticated_user_id,
        approve=approve,
        receipt_root=Path("/absolute/path/to/approved/receipts"),
    )
    return ExtendAPI(client, policy=policy)
```

Every write invokes the host callback separately; decisions expire at the configured timeout and are never cached by the toolkit. Bind any persisted host approval tokens to actor, operation and payload, expire them, and consume them atomically once. A model saying “confirmed” has no authority. The host must authenticate the actor and choose appropriately scoped API credentials; backend authorization still applies.

Receipt uploads reject symlinks, hard links, nonregular files, mismatched signatures and files above the host byte limit (20 MiB by default). They use a stable snapshot before approval. File access fails closed on platforms without safe directory-descriptor opening. Omitting `transaction_id` preserves all file/approval checks and the conservative receipt/transaction capability requirements.

`workflows.upload_and_automatch(api, file_path, max_polls=20)` uploads once, starts one approved job, then polls reads. It returns complete, partial/failed, pending or unknown status with receipt/job identifiers. A pending or uncertain write must be reconciled; the workflow never replays uploads or jobs automatically.

## Optional adapters

Create `ExtendOpenAIToolkit` or `ExtendLangChainToolkit` from `ExtendAPI(client, policy=...)` and register its `get_tools()` with your host. Close the shared API client with `async with` or `aclose()`. LangChain tools use asynchronous `ainvoke`; synchronous invocation is unsupported because it creates incompatible event loops around pooled clients.

Disable optional telemetry before importing providers: `LANGSMITH_TRACING=false` and `OTEL_SDK_DISABLED=true`. OpenAI Agent runs should use `RunConfig(tracing_disabled=True, trace_include_sensitive_data=False)`. Necessary model inputs still go to the selected provider. The toolkit does not change the embedding process's global tracing settings.

## Reference examples

The OpenAI and Anthropic terminal clients demonstrate bounded conversations over local MCP. They are reference examples for host integration. Applications remain responsible for authentication, approval UI, durable state, outcome reconciliation and operational monitoring. Their existing import paths remain available.

```sh
pip install 'extend-ai-toolkit[terminal-openai]'       # or [terminal-anthropic]
python -m extend_ai_toolkit.modelcontextprotocol.client.mcp_client \
  --provider=openai --model=YOUR_MODEL --environment=stage
```

Set the selected provider's API key in the host environment. The terminal launcher starts the read-only stdio server. The example handles native provider messages, multiple tool calls, retained session state, bounded rounds, parallel reads and ordered writes. For embedded servers that permit writes, attempted mutations are recorded for the session, including uncertain/cancelled ones; reconcile their outcome before starting a new session or retrying. This in-memory protection does not persist across process restarts.

The [adapter examples](extend_ai_toolkit/examples/README.md) can also run against synthetic fixtures without credentials or model calls.

## Validation

`make lint` and `make test` run the named safety, adapter, contract and conversation tests. Fixture tests make no live financial requests. The examples accept `--fixture` and need no credentials for that mode. [CONTRACTS.md](CONTRACTS.md) records endpoint evidence and [SANDBOX.md](SANDBOX.md) defines the separate release smoke checks. A passing synthetic test is not production/sandbox validation. Release order and Trusted Publishing setup are documented in [MIGRATION.md](MIGRATION.md).
