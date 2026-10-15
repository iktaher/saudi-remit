#!/usr/bin/env bash
# Single-instance Telegram poller with restart-on-crash. Token is sourced from ./.env (chmod 600, gitignored); never printed.
cd "$(dirname "$0")/.." || exit 1
exec 9>/tmp/whatarrives-bot.lock
flock -n 9 || { echo "$(date '+%F %T') supervisor already running; exiting" >> bot.log; exit 0; }
echo $$ > /tmp/whatarrives-bot.pid
set -a; . ./.env; set +a
while true; do
  python3 -u src/telegram_bot.py poll >> bot.log 2>&1 9>&-
  echo "$(date '+%F %T') poller exited ($?); restarting in 5s" >> bot.log; sleep 5
done
