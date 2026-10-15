#!/usr/bin/env bash
# Single-instance hourly fetch+build+alerts loop. Token from ./.env; never printed.
cd "$(dirname "$0")/.." || exit 1
exec 9>/tmp/whatarrives-alerts.lock
flock -n 9 || { echo "$(date '+%F %T') alerts loop already running; exiting" >> run.log; exit 0; }
echo $$ > /tmp/whatarrives-alerts.pid
set -a; . ./.env; set +a
while true; do ./run.sh >> run.log 2>&1 9>&-; sleep 3600; done
