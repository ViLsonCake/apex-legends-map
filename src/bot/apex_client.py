"""Client for the apexlegendsstatus.com map rotation API."""
import json
import os
import urllib.request

API_URL = "https://api.apexlegendsstatus.com/maprotation?version=2"
TIMEOUT_SECS = 5


class ApexApiError(Exception):
    pass


def fetch_rotation() -> dict:
    request = urllib.request.Request(
        API_URL,
        headers={"Authorization": os.environ["APEX_API_KEY"], "User-Agent": "apex-legends-map-bot"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # network errors, HTTP errors, bad JSON
        raise ApexApiError(f"Failed to fetch map rotation: {exc}") from exc
    if not isinstance(data, dict) or "Error" in data:
        raise ApexApiError(f"Unexpected API response: {data!r}")
    return data
