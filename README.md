# Saudi Remit MVP
Run: `./run.sh` (fetch -> build -> alerts). Output in `site/`. Set `SITE_URL` env for correct canonical/hreflang/sitemap URLs.
- src/fetch_rates.py: mid-market baseline (open.er-api.com, frankfurter fallback) + channel probes. Unscrapable channels = "unavailable"; never invented.
- src/build_site.py + src/i18n.py: 8 languages x (home + 8 currency pages + payday + fee comparison). Translations are short machine drafts: NATIVE REVIEW ADVISED.
- src/telegram_bot.py: `poll` (listener for /alert INR 23.5, /list, /stop), `check` (after fetch), `dry-run`. Needs TELEGRAM_BOT_TOKEN.
- .github/workflows/hourly.yml: hourly build + GitHub Pages deploy.
Note: `poll` must run on an always-on host; GitHub Actions only runs `check`.

## WhatArrives multi-country config
- Sending countries: `src/config.py` → `COUNTRIES` (URLs `/{lang}/{src}-to-{target}/`, e.g. `aed-to-inr`). SAR data: `data/rates.json` (Wise + WU + Saudi apps); others: `data/rates_{src}.json` (Wise public quotes where the route exists, otherwise mid-market only, clearly labelled).
- Optional GitHub repo variables (empty = off): `SITE_URL`, `GSC_VERIFICATION`, `GOATCOUNTER_CODE`, `TELEGRAM_URL` (default https://t.me/Yayamy_helper_ya_bot), `CONTACT_EMAIL`, `CONTACT_ADDRESS` (shown in footer/About/Contact when set), `AFF_WISE_URL`, `AFF_REMITLY_URL`, `AFF_WORLDREMIT_URL`, `AFF_INSTAREM_URL`, `AFF_WU_URL`.
- Affiliate links render only on non-SAR pages, only for providers listed for that sending country in `AFFILIATES[...]["send"]`, with `rel="sponsored nofollow"` and a commission note. Never on SAR pages (SAMA). Ranking is by data only.

## Telegram bot (box)
- Start/restart: `pkill -f scripts/bot-supervisor.sh; pkill -f "telegram_bot.py poll"; setsid nohup scripts/bot-supervisor.sh >/dev/null 2>&1 </dev/null &` (flock on /tmp/whatarrives-bot.lock = single instance; restarts poller on crash). Same for `scripts/alerts-loop.sh` (hourly run.sh + alerts).
- Token lives in `./.env` (chmod 600, gitignored). Commands: `/alert INR 23.5` (SAR), `/alert AED INR 25.9`, `/rate AED INR`, `/list`, `/stop`. Test: `python3 src/telegram_bot.py dry-run` / `getme`.
