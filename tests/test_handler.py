import base64
import json

import pytest

import apex_client
import handler
import telegram_client


@pytest.fixture
def sent(monkeypatch, rotation):
    calls = []
    monkeypatch.setattr(apex_client, "fetch_rotation", lambda: rotation)
    monkeypatch.setattr(telegram_client, "send_photo", lambda c, p, t: calls.append(("photo", c, p, t)))
    monkeypatch.setattr(telegram_client, "send_message", lambda c, t: calls.append(("message", c, t)))
    return calls


def _event(text, secret="s3cret", b64=False):
    body = json.dumps({"update_id": 1, "message": {"chat": {"id": 42}, "text": text}})
    if b64:
        body = base64.b64encode(body.encode()).decode()
    return {"headers": {"x-telegram-bot-api-secret-token": secret}, "body": body, "isBase64Encoded": b64}


def test_rejects_bad_secret(sent):
    assert handler.lambda_handler(_event("/ranked", secret="wrong"), None)["statusCode"] == 401
    assert sent == []


def test_ranked_sends_photo(sent):
    assert handler.lambda_handler(_event("/ranked@MyBot"), None)["statusCode"] == 200
    kind, chat_id, photo, caption = sent[0]
    assert (kind, chat_id) == ("photo", 42)
    assert "E-District" in caption


def test_start_sends_message(sent):
    handler.lambda_handler(_event("/start", b64=True), None)
    assert sent[0][0] == "message"


def test_ignores_non_commands(sent):
    assert handler.lambda_handler(_event("hi there"), None)["statusCode"] == 200
    assert sent == []


def test_photo_failure_falls_back_to_message(monkeypatch, sent):
    def fail(*_):
        raise telegram_client.TelegramError("bad photo")

    monkeypatch.setattr(telegram_client, "send_photo", fail)
    handler.lambda_handler(_event("/pubs"), None)
    assert sent[0][0] == "message" and "Broken Moon" in sent[0][2]


def test_telegram_failure_still_returns_200(monkeypatch, sent):
    def fail(*_):
        raise telegram_client.TelegramError("down")

    monkeypatch.setattr(telegram_client, "send_message", fail)
    assert handler.lambda_handler(_event("/start"), None)["statusCode"] == 200
