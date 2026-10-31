# Focused test sets

Version 2 replaces old adapter tests that mocked the FastMCP constructor/method switch or bypassed policy with `test_adapter_security.py`, which constructs the real optional adapters and invokes their public async entry points. `test_security.py` covers capability parsing, strict inputs, host decisions, confinement and file snapshots. Stable catalog, configuration and package-boundary assertions remain in the core/configuration/packaging tests.

The old ambient-credential integration module was removed: importing it loaded `.env`, and its mutations bypassed the executor. Live validation belongs to the explicit stage-only fixture smoke set in the stacked contracts/client change. It is never part of default CI. Contract and conversation fixtures are added by that change; they replace the old SDK-signature fallback tests.
