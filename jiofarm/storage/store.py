"""JioFarm — SQLite storage layer (v2: analytics-ready)."""

from __future__ import annotations

import sqlite3
import threading


class Store:
    """Thread-safe SQLite store for hunt results + analytics."""

    def __init__(self, path: str = "results.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        with self.lock, self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS hunts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    activation_id TEXT,
                    otp TEXT,
                    logged_in INTEGER DEFAULT 0,
                    link TEXT,
                    cost REAL DEFAULT 0.0,
                    refunded INTEGER DEFAULT 0,
                    link_status TEXT,
                    created_at TEXT DEFAULT (datetime('now'))
                )""")
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS balance_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT,
                    balance REAL,
                    created_at TEXT DEFAULT (datetime('now'))
                )""")
            # migrate older DBs (v1 -> v2)
            cols = {r["name"] for r in self.conn.execute("PRAGMA table_info(hunts)")}
            for name, ddl in (
                ("cost", "ALTER TABLE hunts ADD COLUMN cost REAL DEFAULT 0.0"),
                ("refunded", "ALTER TABLE hunts ADD COLUMN refunded INTEGER DEFAULT 0"),
                ("link_status", "ALTER TABLE hunts ADD COLUMN link_status TEXT"),
            ):
                if name not in cols:
                    self.conn.execute(ddl)

    # --------------------------------------------------------------- writes
    def save(
        self,
        phone: str,
        act_id: str | None,
        otp: str | None,
        logged_in: bool,
        link: str | None,
        cost: float = 0.0,
    ) -> None:
        with self.lock, self.conn:
            self.conn.execute(
                "INSERT INTO hunts (phone, activation_id, otp, logged_in, link, cost) "
                "VALUES (?,?,?,?,?,?)",
                (phone, act_id, otp, int(logged_in), link, cost),
            )

    def mark_refunded(self, act_id: str) -> None:
        """Mark an activation as refunded (balance reclaimed)."""
        with self.lock, self.conn:
            self.conn.execute(
                "UPDATE hunts SET refunded = 1 WHERE activation_id = ? AND refunded = 0",
                (act_id,),
            )

    def set_link_status(self, link: str, status: str) -> None:
        """Set link_status ('valid' / 'dead') for a stored link."""
        with self.lock, self.conn:
            self.conn.execute(
                "UPDATE hunts SET link_status = ? WHERE link = ?",
                (status, link),
            )

    def log_balance(self, provider: str, balance: float) -> None:
        with self.lock, self.conn:
            self.conn.execute(
                "INSERT INTO balance_log (provider, balance) VALUES (?,?)",
                (provider, balance),
            )

    # --------------------------------------------------------------- reads
    def all_links(self) -> list[str]:
        cur = self.conn.execute(
            "SELECT link FROM hunts WHERE link IS NOT NULL AND link != '' "
            "ORDER BY id DESC"
        )
        return [r["link"] for r in cur.fetchall()]

    def recent(self, n: int = 20) -> list[dict]:
        cur = self.conn.execute(
            "SELECT * FROM hunts ORDER BY id DESC LIMIT ?", (n,)
        )
        return [dict(r) for r in cur.fetchall()]

    def balance_history(self, n: int = 100) -> list[dict]:
        cur = self.conn.execute(
            "SELECT * FROM balance_log ORDER BY id DESC LIMIT ?", (n,)
        )
        return [dict(r) for r in cur.fetchall()]

    def stats(self) -> dict:
        cur = self.conn.execute(
            "SELECT COUNT(*) n, SUM(logged_in) logins, "
            "SUM(CASE WHEN link IS NOT NULL AND link != '' THEN 1 ELSE 0 END) links, "
            "SUM(cost) total_cost, SUM(refunded) refunds "
            "FROM hunts"
        )
        row = cur.fetchone()
        n = row["n"] or 0
        links = row["links"] or 0
        total_cost = row["total_cost"] or 0.0
        refunds = row["refunds"] or 0
        net_cost = max(total_cost - refunds * 0.0, 0.0)  # refunds are balance-level, cost kept as spent
        return {
            "hunts": n,
            "logins": row["logins"] or 0,
            "links": links,
            "total_cost": round(total_cost, 4),
            "net_cost": round(net_cost, 4),
            "cost_per_hunt": round(total_cost / n, 4) if n else 0.0,
            "cost_per_link": round(total_cost / links, 4) if links else 0.0,
            "refunds": refunds,
            "hit_rate": round(links / n * 100, 2) if n else 0.0,
        }
