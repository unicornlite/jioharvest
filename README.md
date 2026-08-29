# 🦁 JioHarvest — Google AI Pro / Gemini Pro Link Hunter

> **Fork kencang dari JioFarm v2.0** — Mock provider, analytics, link verification, webhooks multi-channel, dan WebUI monitor. **Zero-dependency dashboard.**

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Rich](https://img.shields.io/badge/terminal-rich-purple.svg)](https://github.com/Textualize/rich)
[![WebUI](https://img.shields.io/badge/WebUI-stdlib-8A2BE2.svg)](https://github.com/unicornlite/jioharvest)
[![Mock](https://img.shields.io/badge/Mock%20DryRun-2ea44f.svg)](https://github.com/unicornlite/jioharvest)

---

## 📖 Apa Ini?

JioHarvest adalah tool otomatis yang:

1. **Menyewa** nomor virtual Jio (India) dari berbagai SMS provider
2. **Login** ke Jio selfcare pakai OTP yang diterima nomor tersebut
3. **Berburu** link redeem Google AI Pro / Gemini Pro dari API subscription Jio
4. **Notifikasi** ke Telegram, Discord, Slack, atau webhook kustom
5. **Pantau** real-time via WebUI zero-dependency (stdlib only, port 9121)

Dilengkapi **live dashboard** berbasis Rich di terminal + **WebUI dark mode** untuk monitoring dari HP.

**JioHarvest vs JioFarm original:**

| Fitur | JioFarm | JioHarvest |
|---|---|---|
| Mock Provider (dev/test) | ❌ | ✅ `--dry-run` |
| Cost per link / Hit Rate | ❌ | ✅ SQLite analytics |
| Link Verification | ❌ | ✅ auto-check validitas |
| Discord / Slack / ntfy | ❌ | ✅ webhooks multi-channel |
| WebUI Monitor | ❌ | ✅ stdlib, zero-dep, port 9121 |
| Multi-provider (Grizzly+5SIM) | ✅ | ✅ + mock provider |

---

## 🖥️ Live Dashboard Preview

```text
┌─ 🦁 JioHarvest Hunter ─────────────────────────────────────────────┐
│ workers: 2 | max-price: $0.5 | refund pending: 0                    │
│ ⏱ 45s elapsed | 💰 $2.50 | 🎯 1 links                              │
└─────────────────────────────────────────────────────────────────────┘
┌─ Workers ────────────────────────────┐ ┌─ 🎯 Links Found ──────────┐
│ W  Phase          Phone    Status    │ │ https://serviceactivation. │
│ 1  ✅ DONE       +91 9876  LINK!     │ │ google.com/...             │
│ 2  ⏳ WAITING_OTP +91 5432  wait...  │ │                            │
└──────────────────────────────────────┘ └────────────────────────────┘
```

### 🌐 WebUI Monitor (zero-dependency)

```text
python -m jiofarm web --port 9121
→ http://127.0.0.1:9121
```

Dark mode, auto-refresh 5s, kartu statistik, tabel hunt real-time. **Bisa dipasang di VPS/LAN dan dibuka dari HP.** Tidak perlu Node.js, tidak perlu FastAPI, tidak perlu dependency tambahan — `http.server` + stdlib.

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/unicornlite/jioharvest.git
cd jioharvest
```

### 2. Setup environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -e .
```

### 3. Test tanpa modal (recommended!)

```bash
python -m jiofarm run --dry-run --count 3 --concurrency 2
```

Mode `--dry-run` menggunakan **Mock Provider** internal — tidak perlu API key, tidak perlu topup, tidak perlu internet ke provider SMS. Cocok untuk testing dan eksperimen.

### 4. Setup nyata

Copy `.env.example` ke `.env`, isi API key provider:

```env
# Pilih provider: grizzlysms, fivesim, mock (untuk testing)
PROVIDER=grizzlysms
GRIZZLY_API_KEY=key_kamu_disini
```

Jalankan:

```bash
python -m jiofarm run --max-price 0.5 --duration 2h
```

---

## 🎮 CLI Commands

| Command | Fungsi |
|---|---|
| `python -m jiofarm` | Interactive menu |
| `python -m jiofarm run --dry-run` | **Test tanpa modal** (Mock Provider) |
| `python -m jiofarm run --count 5 -c 2` | 5 nomor, 2 worker paralel |
| `python -m jiofarm run --duration 6h --target 3` | 6 jam atau sampai 3 link |
| `python -m jiofarm balance` | Cek saldo provider |
| `python -m jiofarm stats` | Statistik + cost/link + hit rate |
| `python -m jiofarm links` | Lihat semua link tersimpan |
| `python -m jiofarm links --out links.txt` | Export ke file |
| `python -m jiofarm web` | **WebUI dashboard** (port 9121) |

### WebUI

```bash
# Dashboard lokal
python -m jiofarm web

# Bind ke LAN (akses dari HP di jaringan yang sama)
python -m jiofarm web --host 0.0.0.0 --port 9121

# Custom database
python -m jiofarm web --db my_results.db
```

---

## 📡 Provider

### Multi-Provider Architecture

JioHarvest support **3 provider** dengan arsitektur Protocol interface. Ganti provider tinggal 1 baris di `.env`:

| Provider | Status | Produk | Harga | Cara |
|---|---|---|---|---|
| **Mock** | ✅ Dev mode | — | $0 | `--dry-run` |
| **GrizzlySMS** | ✅ Ready | `jio` | $0.20–$1.00 | `PROVIDER=grizzlysms` |
| **5SIM** | ⚠️ Partial | `jiomart` | ~$0.05 | `PROVIDER=fivesim` |

Untuk informasi lengkap tentang pemilihan provider, tips nomor fresh, dan cara menambah provider kustom, lihat [dokumentasi provider lengkap](#).

---

## ⚙️ Konfigurasi `.env` Lengkap

| Variable | Default | Deskripsi |
|---|---|---|
| `PROVIDER` | `grizzlysms` | `grizzlysms`, `fivesim`, atau `mock` |
| `GRIZZLY_API_KEY` | — | API key dari GrizzlySMS |
| `FIVESIM_API_KEY` | — | JWT token dari 5SIM |
| `MAX_PRICE` | `1.0` | Harga maks per nomor (USD) |
| `CONCURRENCY` | `2` | Jumlah worker paralel |
| `DB_PATH` | `results.db` | Path database SQLite |
| `TG_BOT_TOKEN` | *(optional)* | Token bot Telegram |
| `TG_CHAT_ID` | *(optional)* | Chat ID Telegram |
| `WEBHOOK_URLS` | *(optional)* | URL Discord/Slack/ntfy (pisahkan dengan koma) |

---

## 🔔 Notifikasi Multi-Channel

Selain Telegram, JioHarvest support **webhook generik** untuk Discord, Slack, ntfy, atau webhook kustom lainnya:

```env
# Discord
WEBHOOK_URLS=https://discord.com/api/webhooks/xxx/yyy

# Discord + Slack barengan
WEBHOOK_URLS=https://discord.com/api/webhooks/xxx/yyy,https://hooks.slack.com/services/xxx/yyy/zzz
```

---

## 📊 Analytics

JioHarvest menyimpan setiap hunt dengan detail:
- Nomor telepon
- Cost per nomor
- Status login & link
- Timestamp

Available via:
- `jiofarm stats` — CLI summary
- `jiofarm web` → `http://localhost:9121/api/stats` — JSON API
- WebUI dashboard — kartu visual

---

## 🧠 Cara Kerja

```
[Mock/Grizzly/5SIM]    [Jio Selfcare]         [Google APIs]
     │                      │                      │
 1. sewa nomor ──────────► 2. kirim OTP             │
     │                 3. terima OTP ◄───┐           │
     │                 4. validate OTP ──┘           │
     │                 5. login sukses ──────────► 6. hunt link
     │                                           7. link ketemu!
     │                      │                      │
 8. complete / refund ◄─────┘                      │
```

Setiap worker menjalankan siklus ini secara paralel. Nomor yang gagal di-refund otomatis oleh `RefundWorker`.

---

## 📁 Project Structure

```
jioharvest/
├── jiofarm/                  # Package Python
│   ├── __init__.py
│   ├── __main__.py           # Entry point
│   ├── cli.py                # Typer CLI + Rich Live Dashboard
│   ├── config.py             # Load .env + dataclass config
│   ├── console.py            # Rich Console + multi-channel notif
│   ├── hunter.py             # Orchestrator hunt cycle (generic/provider-agnostic)
│   ├── shield.py             # DNS-over-HTTPS (Cloudflare)
│   ├── verify.py             # Link verification (baru!)
│   ├── webui.py              # WebUI zero-dependency (baru!)
│   ├── mock/                 # Mock provider untuk testing (baru!)
│   │   ├── __init__.py
│   │   └── client.py
│   ├── grizzly/
│   │   ├── __init__.py
│   │   ├── client.py         # GrizzlySMS API client
│   │   └── refund.py         # Auto-refund worker
│   ├── fivesim/
│   │   ├── __init__.py
│   │   └── client.py         # 5SIM API client
│   ├── jio/
│   │   ├── __init__.py
│   │   ├── auth.py           # Jio OTP login
│   │   ├── check.py          # Validasi subscriber Jio
│   │   └── hunt.py           # Link hunting endpoints
│   └── storage/
│       ├── __init__.py
│       └── store.py          # SQLite + analytics (upgraded)
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🛡️ DNS Shield

Beberapa ISP (terutama di Indonesia) memblokir domain provider SMS via DNS. JioHarvest punya **DNS-over-HTTPS shield** yang me-resolve domain lewat Cloudflare (1.1.1.1), bypass pemblokiran ISP. Aktif otomatis tiap kali `run`.

---

## ⚠️ Disclaimer

- **Grey area** — jual link hasil promo Jio ke non-subscriber melanggar ToS Google. Risiko akun sepenuhnya di tangan pengguna.
- **Bukan bisnis jangka panjang** — promo ini ada batas waktu. Jangan jadikan core business.
- **Pure RNG** — tidak semua nomor dapet link. Hit rate tergantung kualitas nomor provider.

---

## 📜 License

MIT © 2024 — Original by [hirotomasato](https://github.com/hirotomasato/jiofarm). Fork & upgrade by [unicornlite](https://github.com/unicornlite).

---

**🦁 Happy Harvesting! — Provider bagus = hasil bagus. Mock dulu, baru gas.**