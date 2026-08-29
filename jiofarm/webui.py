"""JioFarm — Web UI monitor (zero-dependency, stdlib only).

Serves a live dashboard over HTTP reading the same SQLite DB the hunter
writes to.  No auth by design (local/LAN use) — bind to 127.0.0.1 or use a
reverse proxy if you expose it beyond your network.

Routes:
    /               HTML dashboard (auto-refresh)
    /api/stats      JSON analytics
    /api/hunts      JSON recent hunts
    /api/links      JSON found links

Usage:
    python -m jiofarm web [--port 9121] [--db results.db] [--host 127.0.0.1]
"""

from __future__ import annotations

import json
import sqlite3
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from jiofarm.storage.store import Store

PORT = 9121
HOST = "127.0.0.1"

HTML = """<!doctype html>
<html lang="id">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>🦁 JioFarm Monitor</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #0f1115; color: #e6e6e6; padding: 16px; }
  h1 { font-size: 1.2rem; margin-bottom: 16px; color: #ffd166; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 20px; }
  .card { background: #1a1d24; border: 1px solid #2a2f3a; border-radius: 10px; padding: 14px; }
  .card .label { font-size: .75rem; color: #8b93a3; text-transform: uppercase; letter-spacing: .05em; }
  .card .value { font-size: 1.5rem; font-weight: 700; margin-top: 4px; }
  .green { color: #4ade80; } .red { color: #f87171; } .yellow { color: #fbbf24; } .cyan { color: #22d3ee; }
  h2 { font-size: .95rem; color: #8b93a3; margin: 18px 0 8px; }
  table { width: 100%; border-collapse: collapse; font-size: .85rem; }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #22262f; }
  th { color: #8b93a3; font-weight: 600; }
  td.link-cell { word-break: break-all; max-width: 420px; }
  a { color: #4ade80; text-decoration: none; }
  .status { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: .72rem; font-weight: 700; }
  .s-valid { background: #123524; color: #4ade80; }
  .s-dead { background: #3b1216; color: #f87171; }
  .s-unknown { background: #33311a; color: #fbbf24; }
  .muted { color: #5c6370; }
  footer { margin-top: 24px; font-size: .72rem; color: #5c6370; }
</style>
</head>
<body>
  <h1>🦁 JioFarm Monitor</h1>
  <div class="grid" id="stats"></div>
  <h2>📱 Hunt Terbaru</h2>
  <table>
    <thead><tr><th>#</th><th>Phone</th><th>Status</th><th>Cost</th><th>Link</th><th>Waktu</th></tr></thead>
    <tbody id="hunts"></tbody>
  </table>
  <footer>auto-refresh 5s &middot; JioFarm WebUI (zero-dependency)</footer>
<script>
async function refresh() {
  try {
    const [s, h] = await Promise.all([
      fetch('/api/stats').then(r => r.json()),
      fetch('/api/hunts?n=20').then(r => r.json()),
    ]);
    document.getElementById('stats').innerHTML = [
      ['Total Hunt', s.hunts, ''],
      ['Login Sukses', s.logins, ''],
      ['Link Ditemukan', s.links, 'green'],
      ['Hit Rate', s.hit_rate + '%', 'cyan'],
      ['Total Cost', '$' + s.total_cost.toFixed(2), 'red'],
      ['Cost / Link', '$' + s.cost_per_link.toFixed(3), 'yellow'],
    ].map(([l, v, c]) =>
      `<div class="card"><div class="label">${l}</div><div class="value ${c}">${v}</div></div>`
    ).join('');
    document.getElementById('hunts').innerHTML = h.map(r => `
      <tr>
        <td class="muted">${r.id}</td>
        <td>${r.phone}</td>
        <td>${r.logged_in ? '<span class="s-valid">LOGIN</span>' : '<span class="s-unknown">FAIL</span>'}
            ${r.link_status ? `<span class="s-${r.link_status}">${r.link_status.toUpperCase()}</span>` : ''}</td>
        <td>$${(r.cost || 0).toFixed(2)}</td>
        <td class="link-cell">${r.link ? `<a href="${r.link}" target="_blank">${r.link}</a>` : '<span class="muted">-</span>'}</td>
        <td class="muted">${r.created_at || ''}</td>
      </tr>`).join('');
  } catch (e) { /* server restarting — retry next tick */ }
}
refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    store: Store = None  # type: ignore[assignment]  # set by factory

    def _send(self, code: int, body: bytes, ctype: str = "application/json") -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        path = self.path.split("?")[0]
        try:
            if path in ("/", "/index.html"):
                self._send(200, HTML.encode("utf-8"), "text/html; charset=utf-8")
            elif path == "/api/stats":
                self._send(200, json.dumps(self.store.stats()).encode())
            elif path == "/api/hunts":
                try:
                    n = int(self.path.split("n=")[1].split("&")[0])
                except (IndexError, ValueError):
                    n = 20
                self._send(200, json.dumps(self.store.recent(min(max(n, 1), 200))).encode())
            elif path == "/api/links":
                self._send(200, json.dumps(self.store.all_links()).encode())
            else:
                self._send(404, b'{"error":"not found"}')
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}).encode())

    def log_message(self, *a) -> None:  # silence default logging
        pass


def serve(db_path: str = "results.db", host: str = HOST, port: int = PORT) -> None:
    """Blocking HTTP server.  Call in a thread for non-blocking use."""
    store = Store(db_path)
    handler = type("JioHandler", (Handler,), {"store": store})
    srv = ThreadingHTTPServer((host, port), handler)
    print(f"🦁 JioFarm WebUI → http://{host}:{port}  (db: {db_path})")
    srv.serve_forever()


def serve_background(db_path: str = "results.db", host: str = HOST, port: int = PORT) -> threading.Thread:
    """Start the server in a daemon thread; returns the thread."""
    t = threading.Thread(target=serve, args=(db_path, host, port), daemon=True)
    t.start()
    return t
