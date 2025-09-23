from datetime import datetime, timedelta
import re


def parse_relative_interval(interval_str: str) -> timedelta:
    """Converts a string like '7d', '1m', '1y', '1h' to a timedelta object."""
    match = re.match(r"(\d+)([hdmMyY])", interval_str)
    if not match:
        raise ValueError(f"Invalid relative interval format: {interval_str}")

    value, unit = int(match.group(1)), match.group(2).lower()

    if unit == "h":
        return timedelta(hours=value)
    if unit == "d":
        return timedelta(days=value)
    if unit == "m":
        return timedelta(days=value * 30)
    if unit == "y":
        return timedelta(days=value * 365)
    raise ValueError(f"Unknown time unit in interval string: {unit}")


def get_date_intervals(
    start_date: datetime, end_date: datetime, step_days: int
) -> list[tuple[datetime, datetime]]:
    """Generates a list of date interval tuples (start, end) based on a step in days."""
    if step_days <= 0:
        raise ValueError("The step in days (step_days) must be greater than zero.")

    intervals = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=step_days - 1), end_date)
        intervals.append((current_start, current_end))
        current_start += timedelta(days=step_days)
    return intervals
