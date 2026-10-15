#!/usr/bin/env bash
# One-shot pipeline: fetch (incl. headless browser scrape) -> build -> alerts if token set. Output: ./site
set -euo pipefail
cd "$(dirname "$0")"
PY=python3; [ -x .venv/bin/python ] && PY="$PWD/.venv/bin/python"
cd src
$PY fetch_rates.py
$PY build_site.py
[ -n "${DISABLE_ALERTS:-}" ] || $PY telegram_bot.py check || true
