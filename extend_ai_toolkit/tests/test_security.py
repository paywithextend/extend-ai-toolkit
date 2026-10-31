"""Security regressions using synthetic data and a recording transport."""

import asyncio
import json
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from extend_ai_toolkit import ExecutionPolicy, execute_tool, list_tool_specs
from extend_ai_toolkit.policy import ToolPermissionError
from extend_ai_toolkit.receipts import snapshot_receipt
from extend_ai_toolkit.shared import Configuration, ExtendAPI
from extend_ai_toolkit.shared.tools import tools


@pytest.fixture
def client():
    return SimpleNamespace(
        virtual_cards=SimpleNamespace(
            close_virtual_card=AsyncMock(return_value={"closed": True}),
            get_virtual_cards=AsyncMock(return_value={"items": []}),
        ),
        transactions=SimpleNamespace(
            update_transaction_expense_data=AsyncMock(return_value={}),
            send_receipt_reminder=AsyncMock(return_value={}),
        ),
        api_client=SimpleNamespace(post_multipart=AsyncMock(return_value={"id": "receipt"})),
        aclose=AsyncMock(),
    )


def policy(**kwargs):
    return ExecutionPolicy.from_configuration(Configuration.all_tools(), **kwargs)


async def yes(request):
    return True


@pytest.mark.parametrize(
    "scope",
    [
        "small",
        "all,transactions.read",
        "transactions.send",
        "transactions.read,",
        "transactions.readx",
        " alligator ",
    ],
)
def test_malformed_scopes_fail_closed(scope):
    with pytest.raises(ValueError):
        Configuration.from_tool_str(scope)


def test_catalog_effects_and_send_permission():
    assert len(list_tool_specs(policy=policy())) == 26
    assert len(list_tool_specs()) == 16
    assert len({tool.name for tool in tools}) == 26
    config = Configuration.from_tool_str("transactions.read,receipt_attachments.read")
    assert "send_receipt_reminder" not in policy().restrict(config).allowed_tools
    assert Configuration.from_tool_str("transactions.read, transactions.update").scope[
        0
    ].actions == {"read": True, "update": True}


@pytest.mark.parametrize("name", [t.name for t in tools if t.side_effect_class != "read_only"])
async def test_default_policy_denies_every_write(client, name):
    with pytest.raises(ToolPermissionError):
        await execute_tool(client, name, {})
    client.api_client.post_multipart.assert_not_called()


async def test_forged_catalog_cannot_downgrade_effect(client):
    close = next(t for t in tools if t.name == "close_virtual_card")
    forged = close.model_copy(update={"side_effect_class": "read_only"})
    with pytest.raises(ToolPermissionError):
        await execute_tool(
            client, close.name, {"virtual_card_id": "vc1"}, catalog=[forged], policy=policy()
        )
    client.virtual_cards.close_virtual_card.assert_not_called()


async def test_model_confirmation_and_unknown_arguments_rejected(client):
    for args in (
        {"transaction_id": "t", "data": {}, "user_confirmed_data_values": True},
        {"transaction_id": "t", "data": {}, "approval_token": "forged"},
    ):
        with pytest.raises(ValidationError):
            await execute_tool(
                client,
                "update_transaction_expense_data",
                args,
                policy=policy(actor_id="user", approve=yes),
            )


async def test_strict_boolean(client):
    with pytest.raises(ValidationError):
        await execute_tool(client, "get_transactions", {"receipt_missing": "false"})


async def test_approval_is_per_invocation_and_payload_is_detached(client):
    seen = []
    args = {"transaction_id": "t", "data": {"expenseDetails": []}}

    async def approve(request):
        seen.append(request)
        args["data"]["expenseDetails"].append({"forged": True})
        return True

    host = policy(actor_id="authenticated-user", approve=approve)
    await execute_tool(client, "update_transaction_expense_data", args, policy=host)
    assert client.transactions.update_transaction_expense_data.await_args.args == (
        "t",
        {"expenseDetails": []},
    )
    await execute_tool(
        client, "update_transaction_expense_data", {"transaction_id": "t", "data": {}}, policy=host
    )
    assert seen[0].invocation_id != seen[1].invocation_id
    assert seen[0].actor_id == "authenticated-user"
    assert json.loads(seen[0].arguments_json)["data"] == {"expenseDetails": []}


async def test_denied_expired_and_cancelled_approval_make_no_write(client):
    async def no(request):
        return "true"

    async def slow(request):
        await asyncio.sleep(10)

    for callback in (no, slow):
        with pytest.raises(ToolPermissionError):
            await execute_tool(
                client,
                "close_virtual_card",
                {"virtual_card_id": "v"},
                policy=policy(actor_id="user", approve=callback, approval_timeout=0.01),
            )
    task = asyncio.create_task(
        execute_tool(
            client,
            "close_virtual_card",
            {"virtual_card_id": "v"},
            policy=policy(actor_id="user", approve=slow),
        )
    )
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    client.virtual_cards.close_virtual_card.assert_not_called()


async def test_api_configuration_cannot_expand_policy(client):
    api = ExtendAPI(client).restricted_to(Configuration.all_tools())
    with pytest.raises(ToolPermissionError):
        await api.run("close_virtual_card", virtual_card_id="v")


@pytest.mark.parametrize(
    "kind",
    [
        "outside",
        "parent",
        "symlink",
        "directory_link",
        "hardlink",
        "fifo",
        "signature",
        "oversize",
        "directory",
    ],
)
def test_receipt_rejects_unsafe_files(tmp_path, kind):
    root = tmp_path / "receipts"
    root.mkdir()
    source = root / "ok.pdf"
    source.write_bytes(b"%PDF-1.7 synthetic")
    outside = tmp_path / "outside.pdf"
    outside.write_bytes(b"%PDF-1.7 outside")
    target = root / "bad.pdf"
    if kind == "outside":
        target = outside
    elif kind == "parent":
        target = root / ".." / "outside.pdf"
    elif kind == "symlink":
        target.symlink_to(outside)
    elif kind == "directory_link":
        (root / "link").symlink_to(tmp_path, target_is_directory=True)
        target = root / "link" / "outside.pdf"
    elif kind == "hardlink":
        os.link(outside, target)
    elif kind == "fifo":
        os.mkfifo(target)
    elif kind == "signature":
        target.write_bytes(b"not a receipt")
    elif kind == "oversize":
        target.write_bytes(b"%PDF-" + b"x" * 100)
    elif kind == "directory":
        target.mkdir()
    with pytest.raises(ToolPermissionError):
        snapshot_receipt(policy(receipt_root=root, max_receipt_bytes=30), str(target))


async def test_upload_approval_covers_snapshot_not_replaced_file(client, tmp_path):
    source = tmp_path / "safe.pdf"
    original = b"%PDF-1.7 safe"
    source.write_bytes(original)
    seen = []

    async def approve(request):
        seen.append(json.loads(request.arguments_json))
        source.write_bytes(b"%PDF-1.7 changed after snapshot")
        return True

    async def upload(path, data, files):
        assert path == "/receiptattachments"
        assert data == {"transactionId": "t"}
        assert files["file"][1].read() == original
        return {"id": "r"}

    client.api_client.post_multipart.side_effect = upload
    result = await execute_tool(
        client,
        "create_receipt_attachment",
        {"file_path": str(source), "transaction_id": "t"},
        policy=policy(actor_id="user", approve=approve, receipt_root=tmp_path),
    )
    assert result == {"id": "r"}
    assert seen[0]["file_size"] == len(original)
    assert len(seen[0]["file_sha256"]) == 64


async def test_upload_without_handler_does_not_open_file(client, tmp_path):
    with pytest.raises(ToolPermissionError, match="before reading"):
        await execute_tool(
            client,
            "create_receipt_attachment",
            {"file_path": "missing.pdf", "transaction_id": "t"},
            policy=policy(receipt_root=tmp_path),
        )

def test_cli_defaults_and_explicit_environment(monkeypatch):
    pytest.importorskip("mcp")
    import importlib.metadata
    if importlib.metadata.version("mcp").split(".")[0] != "2":
        pytest.skip("MCP 2 extra tested separately")
    from extend_ai_toolkit.modelcontextprotocol.options import Options
    monkeypatch.setenv("EXTEND_API_KEY", "synthetic")
    monkeypatch.setenv("EXTEND_API_SECRET", "synthetic")
    monkeypatch.delenv("ENV", raising=False)
    with pytest.raises(ValueError):
        Options.from_args([])
    options = Options.from_args(["--environment=stage"])
    assert ExecutionPolicy.from_configuration(Configuration.from_tool_str(options.tools)).allowed_tools == ExecutionPolicy.read_only().allowed_tools
    with pytest.raises(SystemExit):
        Options.from_args(["--api-secret=never-accept-process-credentials"])
