# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-10-27

### Added

- Introduced the `extend_ai_toolkit.shared.auth` module to bridge paywithextend 1.x API-key flows with the new 2.x authorization objects.
- Documented custom authorization usage in the README for paywithextend 2.0 adopters.

### Changed

- All toolkit factories (`ExtendAPI`, framework-specific toolkits, MCP server) now build clients via the compatibility helpers so callers can inject `Authorization` strategies while remaining backwards compatible with API keys.
- `shared.functions.get_transactions` detects the available paywithextend parameters, enabling multi-status filters, receipt and expense category switches, and the new 2.0 field names.
- Updated integration and MCP tests to create clients through the compatibility layer and assert the toolkit version dynamically.
- Raised the dependency pin to `paywithextend==2.0.0` and bumped the package version to 1.3.0.

## [1.2.0] - 2025-04-11

### Added

- Added the `send_receipt_reminder` workflow (schema, prompt, function, and tests) so agents can nudge cardholders about missing receipts.
- Supported the `receipt_missing` filter when listing transactions to mirror the upstream SDK capabilities.
- Expanded the development extras with CrewAI and `pytest-asyncio` dependencies for local agent testing.

### Changed

- Refactored the toolkit constructors to accept a pre-configured `ExtendAPI`, allowing shared clients across OpenAI, LangChain, CrewAI, and MCP servers.
- Adjusted receipt-related scopes, prompts, and tool metadata (including removal of the `match` action) to align with the newest Extend API behavior.
- Broadened dependency ranges (`openai>=1.66.3,<2.0.0`) and bumped the required `paywithextend` SDK to 1.2.1.
- Expanded prompts, schemas, and tests to cover the new receipt-reminder functionality end to end.

### Removed

- Dropped the `MATCH` enum action and associated scope usage.

## [1.1.0] - 2025-04-08

### Added

- Initial public release of the Extend AI Toolkit on PyPI.
- Core `ExtendAPI` async client plus resource helpers for credit cards, virtual cards, transactions, expense categories, and receipt uploads.
- Shared function layer and formatting helpers that power the agent-facing tools across frameworks.
- Ready-to-use integrations for Anthropic MCP, OpenAI Agents, LangChain, and CrewAI, including configuration models and extensive examples.
- Automated packaging assets (pyproject metadata, Makefile targets, GitHub release workflow) and a comprehensive unit/integration test suite.

### Changed

- Updated documentation and packaging instructions to reflect the published distribution (`pip install extend_ai_toolkit`).

### Deprecated

- None (initial release).

### Removed

- None (initial release).

### Fixed

- None (initial release).

### Security

- None (initial release).
