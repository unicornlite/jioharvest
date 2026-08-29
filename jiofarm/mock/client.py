"""JioFarm — Mock SMS Provider for development/testing without spending money.

Simulates GrizzlySMS behaviour so the whole hunt cycle can be exercised
offline: rent → OTP arrives after N seconds → hunt succeeds/fails with a
configurable probability.  Enable with PROVIDER=mock in .env.
"""

from __future__ import annotations

import random
import threading
import time

from jiofarm.config import Config


class MockSMS:
    """Deterministic-ish fake provider.  Same interface as GrizzlySMS."""

    def __init__(self, cfg: Config, log=None):
        self.cfg = cfg
        self.log = log or (lambda _: None)
        self.balance_usd = float(getattr(cfg, "mock_balance", 50.0))
        self._seq = 0
        self._lock = threading.Lock()
        # hunt success probability 0..1
        self.success_rate = float(getattr(cfg, "mock_success_rate", 0.3))
        # seconds before the fake OTP "arrives"
        self.otp_delay = float(getattr(cfg, "mock_otp_delay", 3))
        self.last_cost = 0.0

    # -- provider interface ------------------------------------------------
    def balance(self) -> float:
        return self.balance_usd

    def rent(self, max_price: float | None = None) -> tuple[str, str]:
        price = min((max_price or 0.5), 0.5)
        with self._lock:
            self._seq += 1
            act_id = f"MOCK{self._seq:08d}"
            phone = f"+91{random.randint(7000000000, 9999999999)}"
        self.balance_usd -= price
        self.last_cost = price
        self.log(f"[mock] rented {phone} (${price:.2f}) -> {act_id}")
        return act_id, phone

    def ready(self, act_id: str) -> None:
        # mock auto-activates like 5SIM
        pass

    def status(self, act_id: str) -> tuple[str, str | None]:
        # first call: WAIT; after otp_delay: OK with a fake 6-digit code
        key = f"{act_id}:{int(time.time() // self.otp_delay)}"
        if random.random() < 0.1:  # occasional upstream cancel
            return "CANCEL", None
        return "OK", "".join(str(random.randint(0, 9)) for _ in range(6))

    def complete(self, act_id: str) -> None:
        self.log(f"[mock] completed {act_id}")

    def cancel(self, act_id: str) -> None:
        self.log(f"[mock] cancelled {act_id}")
        self.balance_usd += 0.5  # refund
