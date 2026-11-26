"""AWS Lambda entry point for the Telegram webhook (Lambda Function URL)."""
import base64
import hmac
import json
import os

import telegram_client
from commands import build_reply, parse_command

SECRET_HEADER = "x-telegram-bot-api-secret-token"


def _response(status: int, body: str = "ok") -> dict:
    return {"statusCode": status, "body": body}


def _is_authorized(event: dict) -> bool:
    expected = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    received = headers.get(SECRET_HEADER, "")
    return bool(expected) and hmac.compare_digest(received, expected)


def _parse_body(event: dict) -> dict:
    body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    return json.loads(body)


def send_reply(chat_id: int, reply) -> None:
    if reply.photo_url:
        try:
            telegram_client.send_photo(chat_id, reply.photo_url, reply.text)
            return
        except telegram_client.TelegramError as exc:
            print(f"WARN sendPhoto failed, falling back to sendMessage: {exc}")
    telegram_client.send_message(chat_id, reply.text)


def lambda_handler(event, context):
    if not _is_authorized(event):
        return _response(401, "unauthorized")

    try:
        update = _parse_body(event)
    except (ValueError, UnicodeDecodeError):
        return _response(400, "bad request")

    message = update.get("message") or {}
    command = parse_command(message.get("text"))
    chat_id = (message.get("chat") or {}).get("id")
    if command is None or chat_id is None:
        return _response(200)

    try:
        send_reply(chat_id, build_reply(command))
    except telegram_client.TelegramError as exc:
        print(f"ERROR replying to /{command}: {exc}")
    # Always 200 so Telegram does not retry the update.
    return _response(200)
