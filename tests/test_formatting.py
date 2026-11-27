import pytest

from formatting import format_long_duration


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (176672, "2 days 1 hour and 4 minutes"),  # 49:04:32
        (487791, "5 days 15 hours and 29 minutes"),
        (3600, "1 hour"),
        (86400 + 60, "1 day and 1 minute"),
        (2 * 86400, "2 days"),
        (90, "1 minute"),
        (30, "less than a minute"),
        (0, "less than a minute"),
    ],
)
def test_format_long_duration(seconds, expected):
    assert format_long_duration(seconds) == expected
