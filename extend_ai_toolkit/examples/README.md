# Integration reference examples

These examples show how to register the toolkit with an existing host and call one read tool. They do not run an autonomous agent or provide an application runtime. The host owns credential management, authenticated identity, write approvals and lifecycle cleanup.

Install the corresponding `openai` or `langchain` extra, then run from the repository root:

```sh
python extend_ai_toolkit/examples/openai-agent.py --fixture
python extend_ai_toolkit/examples/langchain-react-agent.py --fixture
```

Fixture mode uses synthetic credentials and an HTTPX mock transport; no API or model request is sent. To read from a real account, omit `--fixture`, select `--environment=stage` or `--environment=prod` explicitly, and supply `EXTEND_API_KEY` and `EXTEND_API_SECRET` through the host environment. Output may contain financial information.

The optional terminal reference clients are documented in the [main README](../../README.md#reference-examples). They use local stdio and the read-only CLI catalog by default. Application code enabling writes must supply a trusted host policy and reconcile uncertain results; session-local duplicate protection is not a durable execution ledger.
