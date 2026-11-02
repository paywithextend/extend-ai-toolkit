"""Safe structured error projections; original SDK exceptions remain inspectable."""

import re

from extend.client import ExtendAPIError, ExtendTransportError
from pydantic import ValidationError

from .policy import ToolPermissionError


def error_payload(error, *, mutation=False):
    if isinstance(error, ExtendAPIError):
        code = {401: "unauthorized", 403: "forbidden", 404: "not_found", 429: "rate_limited"}.get(
            error.status_code, "api_error"
        )
        payload = {"code": code, "status": error.status_code, "request_id": error.request_id}
        if error.retry_after and re.fullmatch(r"[0-9]{1,8}", error.retry_after):
            payload["retry_after_seconds"] = int(error.retry_after)
    elif isinstance(error, ToolPermissionError):
        payload = {"code": "host_policy_denied"}
    elif isinstance(error, (ValidationError, ValueError)):
        payload = {"code": "invalid_arguments"}
    elif isinstance(error, ExtendTransportError):
        payload = {"code": "transport_error"}
    else:
        payload = {"code": "tool_failed"}
    if mutation and (not isinstance(error, (ToolPermissionError, ValidationError, ValueError))):
        payload["action"] = "reconcile_before_retry"
    return {"error": payload}
