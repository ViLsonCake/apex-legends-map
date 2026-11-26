"""Builds replies for each bot command from the map rotation data."""
from dataclasses import dataclass
from html import escape

import apex_client
import templates
from formatting import format_minutes, format_utc

DEFAULT_WILDCARD_EVENT = "wildcard"


@dataclass
class Reply:
    text: str
    photo_url: str | None = None


def _rotation_context(mode: dict) -> dict:
    current, nxt = mode["current"], mode["next"]
    return {
        "map": escape(current["map"]),
        "remaining": escape(current["remainingTimer"]),
        "ends_at": format_utc(current["end"]),
        "next_map": escape(nxt["map"]),
        "next_duration": format_minutes(nxt["DurationInMinutes"]),
        "event_name": escape(current.get("eventName", "")),
        "next_event_name": escape(nxt.get("eventName", "")),
    }


def _mode_reply(template_key: str, mode: dict) -> Reply:
    return Reply(templates.render(template_key, **_rotation_context(mode)), mode["current"].get("asset"))


def start(_rotation=None) -> Reply:
    return Reply(templates.render("start"))


def pubs(rotation: dict) -> Reply:
    return _mode_reply("pubs", rotation["battle_royale"])


def ranked(rotation: dict) -> Reply:
    return _mode_reply("ranked", rotation["ranked"])


def mixtape(rotation: dict) -> Reply:
    return _mode_reply("mixtape", rotation["ltm"])


def wildcard(rotation: dict) -> Reply:
    mode = rotation["wildcard"]
    event_name = mode["current"].get("eventName")
    is_event = bool(event_name) and event_name.strip().lower() != DEFAULT_WILDCARD_EVENT
    return _mode_reply("wildcard_event" if is_event else "wildcard", mode)


# command -> (builder, needs rotation data)
COMMANDS = {
    "start": (start, False),
    "pubs": (pubs, True),
    "ranked": (ranked, True),
    "wildcard": (wildcard, True),
    "mixtape": (mixtape, True),
}


def parse_command(text: str | None) -> str | None:
    """'/Ranked@MyBot extra' -> 'ranked'. Returns None if text isn't a command."""
    if not text or not text.startswith("/"):
        return None
    token = text.split()[0][1:]
    return token.split("@", 1)[0].lower()


def build_reply(command: str) -> Reply:
    entry = COMMANDS.get(command)
    if entry is None:
        return Reply(templates.render("unknown_command"))
    builder, needs_data = entry
    if not needs_data:
        return builder()
    try:
        return builder(apex_client.fetch_rotation())
    except (apex_client.ApexApiError, KeyError, TypeError, ValueError) as exc:
        print(f"ERROR building /{command} reply: {exc!r}")
        return Reply(templates.render("api_error"))
