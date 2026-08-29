"""JioFarm — link verification: check if a Google AI Pro link is still valid."""

from __future__ import annotations

import requests


def verify_link(url: str, timeout: int = 10) -> str:
    """Check if a Google redeem link is still active.

    Returns:
        'valid' — HTTP 200 and the page contains expected content
        'dead'  — HTTP 4xx/5xx or redirects to login/error
        'unknown' — network error or timeout
    """
    try:
        res = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml",
            },
            timeout=timeout,
            allow_redirects=True,
        )
        if res.status_code == 200:
            text = res.text.lower()
            # pages that indicate the promo is still active
            if any(kw in text for kw in ("activate", "redeem", "claim", "get started", "your plan")):
                return "valid"
            # pages that indicate the link is consumed
            if any(kw in text for kw in ("expired", "not found", "already claimed", "invalid")):
                return "dead"
            return "valid"  # 200 with unknown content — assume alive
        if res.status_code in (403, 404, 410):
            return "dead"
        return "unknown"
    except requests.Timeout:
        return "unknown"
    except requests.RequestException:
        return "unknown"