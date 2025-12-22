from __future__ import annotations
from rich.console import Console


def compute_forecast_limits(
    console: Console,
    max_hourly: int,
    max_weekly: int,
) -> tuple[int, int]:
    height = console.size.height
    usable = height - 20

    if usable <= 10:
        hourly, weekly = 4, 3
    elif usable <= 16:
        hourly, weekly = 6, 4
    elif usable <= 22:
        hourly, weekly = 8, 5
    else:
        hourly, weekly = max_hourly, max_weekly

    hourly = max(1, min(hourly, max_hourly))
    weekly = max(1, min(weekly, max_weekly))
    return hourly, weekly


def clamp_text(value: str | None, max_len: int) -> str:
    if not value:
        return ""
    value = str(value)
    return value if len(value) <= max_len else value[: max_len - 1] + "…"