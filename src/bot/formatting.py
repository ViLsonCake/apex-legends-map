"""Time formatting helpers. Unit words come from templates.json."""
import templates

UNITS = (("day", 86400), ("hour", 3600), ("minute", 60))


def format_long_duration(seconds: int) -> str:
    """176672 (49:04:32) -> '2 days 1 hour and 4 minutes'. Seconds are dropped, zero units skipped."""
    words = templates.fmt("long_duration")
    remaining = max(int(seconds), 0)
    parts = []
    for unit, size in UNITS:
        n, remaining = divmod(remaining, size)
        if n:
            parts.append(words[unit if n == 1 else unit + "s"].format(n=n))
    if not parts:
        return words["under_a_minute"]
    if len(parts) == 1:
        return parts[0]
    return words["separator"].join(parts[:-1]) + words["last_separator"] + parts[-1]
