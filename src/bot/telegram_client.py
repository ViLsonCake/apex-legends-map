"""Minimal Telegram Bot API client (stdlib only)."""
import json
import os
import urllib.request

TIMEOUT_SECS = 5


class TelegramError(Exception):
    pass


def call(method: str, payload: dict, token: str | None = None) -> dict:
    token = token or os.environ["TELEGRAM_BOT_TOKEN"]
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/{method}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECS) as response:
            body = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise TelegramError(f"{method} failed: {exc}") from exc
    if not body.get("ok"):
        raise TelegramError(f"{method} failed: {body}")
    return body


def send_message(chat_id: int, text: str) -> dict:
    return call("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def send_photo(chat_id: int, photo_url: str, caption: str) -> dict:
    return call(
        "sendPhoto",
        {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": "HTML"},
    )
