from datetime import datetime
from typing import Dict, Any, Optional


def validate_card_creation_data(
        credit_card_id: str,
        display_name: str,
        balance_cents: int,
        recipient_email: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_to: Optional[str] = None,
        notes: Optional[str] = None
) -> Dict[str, Any]:
    """Validate and format card creation data"""
    if balance_cents <= 0:
        raise ValueError("Balance must be greater than 0")

    if not display_name:
        raise ValueError("Display name is required")

    data = {
        "creditCardId": credit_card_id,
        "displayName": display_name,
        "balanceCents": balance_cents
    }

    if recipient_email:
        data["recipient"] = recipient_email

    if valid_from:
        try:
            # Validate date format
            datetime.strptime(valid_from, "%Y-%m-%d")
            data["validFrom"] = f"{valid_from}T00:00:00.000Z"
        except ValueError:
            raise ValueError("valid_from must be in YYYY-MM-DD format")

    if valid_to:
        try:
            # Validate date format
            datetime.strptime(valid_to, "%Y-%m-%d")
            data["validTo"] = f"{valid_to}T23:59:59.999Z"
        except ValueError:
            raise ValueError("valid_to must be in YYYY-MM-DD format")

    if notes:
        data["notes"] = notes

    return data


def validate_recurrence_data(
        balance_cents: int,
        period: Optional[str] = None,
        interval: Optional[int] = None,
        terminator: Optional[str] = None,
        count: Optional[int] = None,
        until: Optional[str] = None,
        by_week_day: Optional[int] = None,
        by_month_day: Optional[int] = None,
        by_year_day: Optional[int] = None
) -> Dict[str, Any]:
    """Validate and format recurrence data"""
    valid_periods = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
    valid_terminators = ["NONE", "COUNT", "DATE", "COUNT_OR_DATE"]

    if period not in valid_periods:
        raise ValueError(f"Period must be one of: {', '.join(valid_periods)}")

    if terminator not in valid_terminators:
        raise ValueError(f"Terminator must be one of: {', '.join(valid_terminators)}")

    if interval is not None and interval <= 0:
        raise ValueError("Interval must be greater than 0")

    data = {
        "balanceCents": balance_cents,
        "period": period,
        "interval": interval,
        "terminator": terminator
    }

    # Validate terminator-specific fields
    if terminator in ["COUNT", "COUNT_OR_DATE"]:
        if count is None or count <= 0:
            raise ValueError("Count must be provided and greater than 0")
        data["count"] = count

    if terminator in ["DATE", "COUNT_OR_DATE"]:
        if not until:
            raise ValueError("Until date must be provided")
        try:
            datetime.strptime(until, "%Y-%m-%d")
            data["until"] = f"{until}T23:59:59.999Z"
        except ValueError:
            raise ValueError("Until date must be in YYYY-MM-DD format")

    # Validate period-specific fields
    if period == "WEEKLY":
        if by_week_day is None or not 0 <= by_week_day <= 6:
            raise ValueError("by_week_day must be between 0 and 6 (Monday to Sunday)")
        data["byWeekDay"] = by_week_day

    elif period == "MONTHLY":
        if by_month_day is None or not 1 <= by_month_day <= 31:
            raise ValueError("by_month_day must be between 1 and 31")
        data["byMonthDay"] = by_month_day

    elif period == "YEARLY":
        if by_year_day is None or not 1 <= by_year_day <= 365:
            raise ValueError("by_year_day must be between 1 and 365")
        data["byYearDay"] = by_year_day

    return data
