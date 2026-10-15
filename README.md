# Saudi Remit MVP
Run: `./run.sh` (fetch -> build -> alerts). Output in `site/`. Set `SITE_URL` env for correct canonical/hreflang/sitemap URLs.
- src/fetch_rates.py: mid-market baseline (open.er-api.com, frankfurter fallback) + channel probes. Unscrapable channels = "unavailable"; never invented.
- src/build_site.py + src/i18n.py: 8 languages x (home + 8 currency pages + payday + fee comparison). Translations are short machine drafts: NATIVE REVIEW ADVISED.
- src/telegram_bot.py: `poll` (listener for /alert INR 23.5, /list, /stop), `check` (after fetch), `dry-run`. Needs TELEGRAM_BOT_TOKEN.
- .github/workflows/hourly.yml: hourly build + GitHub Pages deploy.
Note: `poll` must run on an always-on host; GitHub Actions only runs `check`.
