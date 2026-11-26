import json
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "maprotation.json"


@pytest.fixture
def rotation():
    return json.loads(FIXTURE.read_text())


@pytest.fixture(autouse=True)
def env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("APEX_API_KEY", "test-key")
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "s3cret")
