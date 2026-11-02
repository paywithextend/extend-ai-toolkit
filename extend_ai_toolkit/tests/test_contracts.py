"""Synthetic wire contracts verified against current Extend controller/DTO source."""

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from extend import ExtendClient
from extend.auth import BasicAuth
from extend.client import ExtendAPIError, ExtendTransportError
from pydantic import ValidationError

from extend_ai_toolkit import ExecutionPolicy, execute_tool
from extend_ai_toolkit.errors import error_payload
from extend_ai_toolkit.shared import Configuration, ExtendAPI
from extend_ai_toolkit.shared.filters import transaction_query
from extend_ai_toolkit.shared.helpers import format_credit_card_detail, format_transactions_list
from extend_ai_toolkit.shared.tools import tools
from extend_ai_toolkit.workflows import upload_and_automatch

CASES = json.loads(Path(__file__).with_name("fixtures").joinpath("contracts.json").read_text())


async def yes(request):
    return True


def host_policy(root=None):
    return ExecutionPolicy.from_configuration(
        Configuration.all_tools(), actor_id="fixture-user", approve=yes, receipt_root=root
    )


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
async def test_every_tool_wire_contract(case, tmp_path):
    (tmp_path / "synthetic.pdf").write_bytes(b"%PDF-1.7 synthetic fixture")
    seen = []
    response = {"id": "fixture", "currency": "EUR", "optional": None}
    if case["name"] == "get_credit_card_detail":
        response = {"creditCard": {"id": "cc_1", "features": {"direct": False}, "currency": "EUR"}}
    elif case["name"] == "get_expense_policy":
        response = {
            "id": "policy",
            "organizationId": "org_1",
            "fileName": "policy.pdf",
            "contentType": "application/pdf",
            "urls": {"original": "https://example.invalid/signed"},
        }
    elif case["name"] == "count_transactions":
        response = {"count": 42}
    elif case["name"] == "get_automatch_status":
        response = {
            "id": "job_1",
            "tasks": [{"id": "task", "status": "SKIPPED", "receiptAttachmentId": "ra_1"}],
        }
    elif case["name"] in {"get_transaction_detail", "update_transaction_expense_data"}:
        response = {
            "id": "t_1",
            "clearingBillingAmountCents": None,
            "authBillingAmountCents": 123,
            "authBillingCurrency": "CAD",
        }
    if case["name"] == "get_transactions":
        response = {"report": {"page": 1, "perPage": 50, "count": 0, "transactions": []}}

    def respond(request):
        seen.append(request)
        assert request.method == case["method"]
        assert request.url.path == case["path"]
        assert dict(request.url.params) == case["query"]
        if case["body"] == "multipart":
            assert b"application/pdf" in request.content
            assert b"transactionId" not in request.content
            assert b"%PDF-1.7" in request.content
        elif case["body"] is not None:
            assert json.loads(request.content) == case["body"]
        return httpx.Response(200, json=response)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        async with ExtendClient(
            auth=BasicAuth("synthetic-key", "synthetic-secret"),
            environment="stage",
            http_client=transport,
        ) as client:
            result = await execute_tool(
                client, case["name"], case["arguments"], policy=host_policy(tmp_path)
            )
    assert len(seen) == 1
    for key, value in response.items():
        assert result[key] == value


def test_fixture_covers_exact_catalog():
    assert {case["name"] for case in CASES} == {tool.name for tool in tools}


async def test_list_count_filter_equivalence_and_repeated_statuses():
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, json={"report": {"transactions": []}})

    filters = {
        "statuses": ["pending", "cleared"],
        "from_date": "2026-01-01",
        "to_date": "2026-02-01",
        "date_type": "Clear",
        "credit_card_id": "cc_1",
        "receipt_statuses": ["missing"],
        "expense_category_statuses": ["attached"],
        "virtual_card_id": "vc_1",
        "min_amount_cents": 0,
        "max_amount_cents": 999,
        "search_term": "synthetic",
    }
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        async with ExtendClient(
            auth=BasicAuth("k", "s"), environment="stage", http_client=transport
        ) as client:
            await execute_tool(client, "get_transactions", filters)
            await execute_tool(client, "count_transactions", filters)
    first = [
        (k, v) for k, v in requests[0].url.params.multi_items() if k not in {"page", "perPage"}
    ]
    assert first == requests[1].url.params.multi_items()
    assert requests[0].url.params.get_list("status") == ["PENDING", "CLEARED"]
    assert requests[0].url.params["sinceClearedAt"] == "2026-01-01"
    assert "since" not in requests[0].url.params
    assert requests[0].url.params["creditCardId"] == "cc_1"
    assert requests[0].url.params["receiptStatus"] == "Missing"
    assert requests[0].url.params["expenseCategoryStatuses"] == "Attached"


@pytest.mark.parametrize(
    "arguments",
    [
        {"statuses": []},
        {"status": "CLEARED", "statuses": ["PENDING"]},
        {"receipt_statuses": ["unknown"]},
        {"receipt_missing": True, "receipt_statuses": ["Attached"]},
        {"from_date": "2026-02-31"},
        {"from_date": "2026-02-01", "to_date": "2026-01-01"},
        {"min_amount_cents": 100, "max_amount_cents": 10},
        {"sort_field": "ignored"},
        {"page": 0},
    ],
)
async def test_filters_fail_before_network(arguments):
    with pytest.raises((ValidationError, ValueError)):
        await execute_tool(object(), "get_transactions", arguments)


def test_false_missing_filters_are_not_dropped():
    assert transaction_query(receipt_missing=False)["receiptStatus"] == ["Attached"]
    assert transaction_query(missing_expense_categories=False)["expenseCategoryStatuses"] == [
        "Attached"
    ]


async def test_full_page_is_provisional_and_advances_once():
    api = SimpleNamespace(
        get_transactions=AsyncMock(
            return_value={
                "report": {
                    "page": 1,
                    "perPage": 1,
                    "count": 2,
                    "transactions": [
                        {
                            "id": "t",
                            "clearingBillingAmountCents": 123,
                            "clearingBillingCurrency": "EUR",
                        }
                    ],
                }
            }
        )
    )
    result = await execute_tool(
        SimpleNamespace(transactions=api), "get_transactions", {"per_page": 1}
    )
    assert result["paginationInfo"] == {
        "page": 1,
        "perPage": 1,
        "countExact": False,
        "mayHaveMore": True,
        "nextPage": 2,
    }
    assert "EUR" in format_transactions_list(result)
    assert "countExact" in format_transactions_list(result)
    assert (
        json.loads(format_credit_card_detail({"creditCard": {"id": "cc", "features": None}}))[
            "creditCard"
        ]["features"]
        is None
    )


async def test_typed_errors_survive_wrappers_and_mcp_redacts():
    def respond(request):
        return httpx.Response(
            403, json={"secret": "sensitive-response"}, headers={"x-request-id": "safe-id"}
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        async with ExtendClient(
            auth=BasicAuth("k", "s"), environment="stage", http_client=transport
        ) as client:
            with pytest.raises(ExtendAPIError) as caught:
                await execute_tool(client, "get_credit_card_detail", {"credit_card_id": "cc"})
            assert error_payload(caught.value) == {
                "error": {"code": "forbidden", "status": 403, "request_id": "safe-id"}
            }
            import importlib.metadata
            import importlib.util

            if (
                importlib.util.find_spec("mcp") is None
                or importlib.metadata.version("mcp").split(".")[0] != "2"
            ):
                return
            from extend_ai_toolkit.modelcontextprotocol.server import ExtendMCPServer

            result = await ExtendMCPServer(ExtendAPI(client)).call_tool(
                "get_credit_card_detail", {"credit_card_id": "cc"}
            )
            assert result.structured_content["error"]["code"] == "forbidden"
            assert "sensitive-response" not in str(result)


@pytest.mark.parametrize(
    "tasks,outcome",
    [
        ([{"status": "SUCCESS"}], "complete"),
        ([{"status": "FAILED"}], "partial_or_failed"),
        ([{"status": "PENDING"}], "pending"),
    ],
)
async def test_receipt_flow_polls_without_replaying_writes(tasks, outcome):
    execute = AsyncMock(side_effect=[{"id": "ra"}, {"id": "job"}, {"id": "job", "tasks": tasks}])
    result = await upload_and_automatch(
        SimpleNamespace(execute=execute), "synthetic.pdf", max_polls=1, interval=0
    )
    assert result["outcome"] == outcome
    assert [call.args[0] for call in execute.await_args_list] == [
        "create_receipt_attachment",
        "automatch_receipts",
        "get_automatch_status",
    ]
    assert execute.await_args_list[0].args[1] == {"file_path": "synthetic.pdf"}


async def test_receipt_write_timeout_is_not_retried():
    execute = AsyncMock(side_effect=ExtendTransportError("uncertain"))
    with pytest.raises(ExtendTransportError):
        await upload_and_automatch(SimpleNamespace(execute=execute), "synthetic.pdf")
    assert execute.await_count == 1


async def test_expense_update_rejects_unadvertised_fields_before_approval():
    approve = AsyncMock(return_value=True)
    policy = ExecutionPolicy.from_configuration(
        Configuration.all_tools(), actor_id="u", approve=approve
    )
    with pytest.raises(ValidationError):
        await execute_tool(
            object(),
            "update_transaction_expense_data",
            {"transaction_id": "t", "data": {"expenseDetails": [], "unexpected": True}},
            policy=policy,
        )
    approve.assert_not_called()


def test_generated_docs_match_catalog():
    import runpy

    generate = runpy.run_path(
        str(Path(__file__).resolve().parents[2] / "tools/generate_capabilities.py")
    )["render"]
    assert Path(__file__).resolve().parents[2].joinpath("CAPABILITIES.md").read_text() == generate()


async def test_explicit_label_clear_is_approved_and_sent_unchanged():
    approved = []
    sent = []

    async def approve(request):
        approved.append(json.loads(request.arguments_json))
        return True

    def respond(request):
        sent.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "t_1", "expenseDetails": []})

    arguments = {
        "transaction_id": "t_1",
        "data": {"expenseDetails": [{"categoryId": "ec_1", "labelId": None}]},
    }
    policy = ExecutionPolicy.from_configuration(
        Configuration.all_tools(), actor_id="u", approve=approve
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        async with ExtendClient(
            BasicAuth("synthetic", "secret"), environment="stage", http_client=transport
        ) as client:
            await execute_tool(client, "update_transaction_expense_data", arguments, policy=policy)
    assert approved == [arguments]
    assert sent == [arguments["data"]]


async def test_label_clear_requires_explicit_label_value():
    with pytest.raises(ValidationError):
        await execute_tool(
            object(),
            "update_transaction_expense_data",
            {"transaction_id": "t", "data": {"expenseDetails": [{"categoryId": "ec"}]}},
            policy=host_policy(),
        )


@pytest.mark.parametrize("name,arguments,wire", [
    ("get_expense_categories", {"transaction_id":"t_1", "required_for_transactions":False}, {"transactionId":"t_1", "requiredForTransactions":"false"}),
    ("create_expense_category", {"name":"Synthetic", "code":"SYN", "required":False, "required_for_transactions":True}, {"name":"Synthetic", "code":"SYN", "required":False, "requiredForTransactions":True}),
    ("update_expense_category", {"category_id":"ec_1", "required_for_virtual_cards":False}, {"requiredForVirtualCards":False}),
])
async def test_custom_field_consumer_contracts(name, arguments, wire):
    seen = []

    def respond(request):
        seen.append(request)
        assert (dict(request.url.params) if request.method == "GET" else json.loads(request.content)) == wire
        return httpx.Response(200, json={})

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        async with ExtendClient(BasicAuth("synthetic", "secret"), environment="stage", http_client=transport) as client:
            await execute_tool(client, name, arguments, policy=host_policy())
    assert len(seen) == 1


@pytest.mark.parametrize("max_polls", [1.5, True, "2"])
async def test_invalid_poll_limit_rejected_before_upload(max_polls):
    from extend_ai_toolkit.workflows import upload_and_automatch

    api = SimpleNamespace(execute=AsyncMock(return_value={"id": "synthetic", "tasks": []}))
    with pytest.raises(ValueError):
        await upload_and_automatch(api, "synthetic.png", max_polls=max_polls)
    api.execute.assert_not_awaited()


@pytest.mark.parametrize("interval", [True, "1", float("nan"), float("inf")])
async def test_invalid_poll_interval_rejected_before_upload(interval):
    api = SimpleNamespace(execute=AsyncMock())
    with pytest.raises(ValueError):
        await upload_and_automatch(api, "synthetic.png", interval=interval)
    api.execute.assert_not_awaited()


@pytest.mark.parametrize("failed_step", ["create_automatch", "poll_status"])
async def test_receipt_flow_retains_completed_step_ids_and_cause(failed_step):
    from extend_ai_toolkit.workflows import ReceiptWorkflowError

    cause = ExtendTransportError("synthetic transport failure")
    responses = [{"id": "ra_recover", "urls": {"original": "sensitive-url"}}]
    if failed_step == "poll_status":
        responses.append({"id": "job_recover"})
    execute = AsyncMock(side_effect=[*responses, cause])
    with pytest.raises(ReceiptWorkflowError) as raised:
        await upload_and_automatch(SimpleNamespace(execute=execute), "synthetic.pdf")
    error = raised.value
    assert error.receipt_id == "ra_recover"
    assert error.job_id == ("job_recover" if failed_step == "poll_status" else None)
    assert error.failed_step == failed_step
    assert error.__cause__ is cause
    assert "sensitive-url" not in str(error)
    assert execute.await_count == len(responses) + 1
    if error.job_id:
        execute.side_effect = None
        execute.return_value = {"id": error.job_id, "tasks": [{"status": "SUCCESS"}]}
        await execute("get_automatch_status", {"job_id": error.job_id})
        assert [call.args[0] for call in execute.await_args_list].count("create_receipt_attachment") == 1
        assert [call.args[0] for call in execute.await_args_list].count("automatch_receipts") == 1


@pytest.mark.parametrize("failed_step", ["create_automatch", "poll_status"])
async def test_receipt_cancellation_retains_ids_and_cancellation_semantics(failed_step):
    import asyncio

    from extend_ai_toolkit.workflows import ReceiptWorkflowCancelled

    cause = asyncio.CancelledError()
    responses = [{"id": "ra_recover"}]
    if failed_step == "poll_status":
        responses.append({"id": "job_recover"})
    execute = AsyncMock(side_effect=[*responses, cause])
    with pytest.raises(asyncio.CancelledError) as raised:
        await upload_and_automatch(SimpleNamespace(execute=execute), "synthetic.pdf")
    assert isinstance(raised.value, ReceiptWorkflowCancelled)
    assert raised.value.receipt_id == "ra_recover"
    assert raised.value.job_id == ("job_recover" if failed_step == "poll_status" else None)
    assert raised.value.failed_step == failed_step
    assert raised.value.__cause__ is cause
    assert execute.await_count == len(responses) + 1
