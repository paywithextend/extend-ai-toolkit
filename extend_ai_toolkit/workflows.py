"""Bounded receipt orchestration using the same host approval policy."""

import asyncio


class ReceiptWorkflowError(RuntimeError):
    """A failed workflow with identifiers from successfully completed steps."""

    def __init__(self, receipt_id: str, job_id: str | None, failed_step: str):
        self.receipt_id = receipt_id
        self.job_id = job_id
        self.failed_step = failed_step
        super().__init__(f"Receipt workflow failed during {failed_step}; reconcile before retrying")


class ReceiptWorkflowCancelled(asyncio.CancelledError):
    """Cancellation retaining completed-step IDs without suppressing cancellation."""

    def __init__(self, receipt_id: str, job_id: str | None, failed_step: str):
        self.receipt_id = receipt_id
        self.job_id = job_id
        self.failed_step = failed_step
        super().__init__("Receipt workflow cancelled; reconcile completed steps before retrying")


async def upload_and_automatch(api, file_path: str, *, max_polls: int = 20, interval: float = 1):
    """Upload once, start one job, and poll read-only status without replaying writes.

    Exhausting the poll budget returns a pending result with receipt/job identifiers.
    Failures after upload raise ReceiptWorkflowError with completed-step identifiers
    and the original cause. Cancellation retains the same state in
    ReceiptWorkflowCancelled, which remains an asyncio.CancelledError.
    Upload failures propagate unchanged because no identifier has been received.
    """
    if (
        type(max_polls) is not int or not 1 <= max_polls <= 120
        or type(interval) not in (int, float) or not 0 <= interval <= 30
    ):
        raise ValueError("Polling limits are out of range")
    receipt = await api.execute("create_receipt_attachment", {"file_path": file_path})
    receipt_id = receipt["id"]
    job_id = None
    failed_step = "create_automatch"
    try:
        job = await api.execute("automatch_receipts", {"receipt_attachment_ids": [receipt["id"]]})
        job_id = job["id"]
        failed_step = "poll_status"
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
    except asyncio.CancelledError as exc:
        raise ReceiptWorkflowCancelled(receipt_id, job_id, failed_step) from exc
    except Exception as exc:
        raise ReceiptWorkflowError(receipt_id, job_id, failed_step) from exc
