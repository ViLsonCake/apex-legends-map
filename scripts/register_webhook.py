"""Registers the Lambda Function URL as the Telegram webhook and publishes the command menu.

Usage: python scripts/register_webhook.py <function_url>
Env:   TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "bot"))

import telegram_client  # noqa: E402
import templates  # noqa: E402


def main(url: str) -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    telegram_client.call(
        "setWebhook",
        {
            "url": url,
            "secret_token": os.environ["TELEGRAM_WEBHOOK_SECRET"],
            "allowed_updates": ["message"],
        },
        token=token,
    )
    commands = [{"command": c, "description": d} for c, d in templates.command_descriptions().items()]
    telegram_client.call("setMyCommands", {"commands": commands}, token=token)
    print(f"Webhook set to {url} and {len(commands)} commands registered")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
