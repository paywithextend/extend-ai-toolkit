"""Opt-in stage-only release validation; never consumes production/ambient SDK credentials."""

import argparse
import asyncio
import json
import os
from pathlib import Path

from extend import ExtendClient
from extend.auth import BasicAuth

from extend_ai_toolkit import ExecutionPolicy
from extend_ai_toolkit.shared import Configuration, ExtendAPI


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--include-writes", action="store_true")
    args = parser.parse_args()
    fixture = json.loads(args.fixture.read_text())
    if fixture.get("environment") != "stage" or fixture.get("synthetic") is not True:
        raise ValueError("Fixture must identify a synthetic stage account")
    root = args.fixture.parent.resolve()
    receipt_name = fixture["receipt_filename"]
    if Path(receipt_name).name != receipt_name:
        raise ValueError("Receipt must be a filename within the fixture directory")
    expected_expense = {
        "transaction_id": fixture["transaction_id"],
        "data": fixture["expense_data"],
    }

    async def approve(request):
        payload = json.loads(request.arguments_json)
        if not args.include_writes:
            return False
        if request.tool_name == "update_transaction_expense_data":
            return payload == expected_expense
        if request.tool_name == "create_receipt_attachment":
            return payload["file_path"] == receipt_name
        if request.tool_name == "automatch_receipts":
            return payload["receipt_attachment_ids"] == uploaded_ids
        return False

    uploaded_ids = []
    policy = ExecutionPolicy.from_configuration(
        Configuration.all_tools(), actor_id=fixture["actor_id"], approve=approve, receipt_root=root
    )
    async with ExtendClient(
        auth=BasicAuth(
            os.environ["EXTEND_SANDBOX_API_KEY"], os.environ["EXTEND_SANDBOX_API_SECRET"]
        ),
        environment="stage",
    ) as sdk:
        api = ExtendAPI(sdk, policy=policy)
        for name, arguments in [
            ("get_organizations", {}),
            ("get_credit_card_detail", {"credit_card_id": fixture["credit_card_id"]}),
            ("get_transactions", {"per_page": 1}),
            ("get_expense_policy", {"organization_id": fixture["organization_id"]}),
        ]:
            await api.execute(name, arguments)
            print(json.dumps({"check": name, "status": "passed"}))
        if args.include_writes:
            await api.execute("update_transaction_expense_data", expected_expense)
            receipt = await api.execute("create_receipt_attachment", {"file_path": receipt_name})
            uploaded_ids.append(receipt["id"])
            job = await api.execute("automatch_receipts", {"receipt_attachment_ids": uploaded_ids})
            for index in range(20):
                status = await api.execute("get_automatch_status", {"job_id": job["id"]})
                states = {task["status"] for task in status["tasks"]}
                if states and "PENDING" not in states:
                    if states != {"SUCCESS"}:
                        raise RuntimeError(
                            "Receipt smoke did not complete successfully; reconcile fixture artifacts"
                        )
                    break
                if index == 19:
                    raise RuntimeError("Receipt job remains pending; reconcile fixture artifacts")
                await asyncio.sleep(1)
            print(json.dumps({"check": "expense_and_receipt_flow", "status": "passed"}))
        else:
            print(json.dumps({"check": "controlled_writes", "status": "not_run"}))


if __name__ == "__main__":
    asyncio.run(main())
