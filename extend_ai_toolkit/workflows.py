"""Bounded receipt orchestration using the same host approval policy."""

import asyncio


async def upload_and_automatch(api, file_path: str, *, max_polls: int = 20, interval: float = 1):
    """Upload once, start one job, and poll read-only status without replaying writes.

    A timeout returns the job and receipt identifiers for later reconciliation.
    Transport failures propagate; callers must reconcile before repeating writes.
    """
    if not 1 <= max_polls <= 120 or not 0 <= interval <= 30:
        raise ValueError("Polling limits are out of range")
    receipt = await api.execute("create_receipt_attachment", {"file_path": file_path})
    job = await api.execute("automatch_receipts", {"receipt_attachment_ids": [receipt["id"]]})
    for index in range(max_polls):
        status = await api.execute("get_automatch_status", {"job_id": job["id"]})
        tasks = status.get("tasks", [])
        states = {task.get("status") for task in tasks}
        if tasks and states <= {"SUCCESS", "FAILED", "SKIPPED"}:
            outcome = "complete" if states == {"SUCCESS"} else "partial_or_failed"
            return {"outcome": outcome, "receipt": receipt, "job": status}
        if states - {"PENDING", "SUCCESS", "FAILED", "SKIPPED"}:
            return {"outcome": "unknown_status", "receipt": receipt, "job": status}
        if index + 1 < max_polls:
            await asyncio.sleep(interval)
    return {"outcome": "pending", "receipt": receipt, "job": status}
