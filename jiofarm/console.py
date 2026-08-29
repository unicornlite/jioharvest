"""JioFarm — Rich console helpers + multi-channel notifications."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.theme import Theme

# Force UTF-8 on Windows so emoji don't crash with cp1252
if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

THEME = Theme(
    {
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "info": "cyan",
        "highlight": "magenta",
        "link": "bold green on black",
        "phase": "bold cyan",
        "dim": "dim",
        "counter": "bold white",
    }
)

console = Console(theme=THEME, highlight=False, force_terminal=True)


def tg_send(msg: str, bot_token: str = "", chat_id: str = "") -> None:
    """Send a Telegram alert (non-blocking, best-effort)."""
    if not bot_token or not chat_id:
        return
    try:
        import requests

        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": msg},
            timeout=15,
        )
    except Exception:
        pass


def webhook_send(msg: str, url: str = "") -> None:
    """Send an alert to a generic webhook (Discord / Slack / ntfy / custom).

    Discord & Slack accept a JSON payload with 'content'; a raw URL is treated
    as an ntfy-style POST where the body IS the message.
    """
    if not url:
        return
    try:
        import requests

        # Discord / Slack
        if "discord.com" in url or "hooks.slack.com" in url:
            requests.post(url, json={"content": msg}, timeout=15)
        else:
            # ntfy / generic: POST raw text
            requests.post(url, data=msg.encode("utf-8"), timeout=15)
    except Exception:
        pass


def notify_all(msg: str, cfg) -> None:
    """Send to every configured channel (Telegram + webhooks)."""
    tg_send(msg, cfg.tg_bot_token, cfg.tg_chat_id)
    for url in getattr(cfg, "webhook_urls", []) or []:
        webhook_send(msg, url)
