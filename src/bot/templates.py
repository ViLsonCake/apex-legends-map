"""Loads every user-facing string from templates.json (the single source of truth)."""
import json
from functools import lru_cache
from pathlib import Path

TEMPLATES_PATH = Path(__file__).with_name("templates.json")


@lru_cache(maxsize=1)
def load() -> dict:
    with TEMPLATES_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def render(key: str, **context) -> str:
    return load()["messages"][key].format(**context)


def fmt(key: str) -> str:
    return load()["formats"][key]


def command_descriptions() -> dict:
    return dict(load()["commands"])
