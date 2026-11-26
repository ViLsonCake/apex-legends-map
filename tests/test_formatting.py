from formatting import format_minutes, format_utc


def test_format_utc():
    assert format_utc(1795662000) == "03:00 UTC, Nov 26"


def test_format_minutes():
    assert format_minutes(90) == "1h 30m"
    assert format_minutes(270) == "4h 30m"
    assert format_minutes(15) == "15m"
    assert format_minutes(120) == "2h"
