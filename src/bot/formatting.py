"""Time formatting helpers. Format strings come from templates.json."""
from datetime import datetime, timezone

import templates


def format_utc(epoch: int) -> str:
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc).strftime(templates.fmt("datetime"))


def format_minutes(total_minutes: int) -> str:
    hours, minutes = divmod(int(total_minutes), 60)
    if hours and minutes:
        return templates.fmt("duration_hours_minutes").format(hours=hours, minutes=minutes)
    if hours:
        return templates.fmt("duration_hours").format(hours=hours)
    return templates.fmt("duration_minutes").format(minutes=minutes)
