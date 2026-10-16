#!/usr/bin/env bash
# Back up the analytics database to ./backups (the newest KEEP copies are kept, default 14).
# Run it from cron, e.g. daily:  0 3 * * * cd ~/openbirddatabase && ./backup.sh >> backup.log 2>&1
# Restore: see docs/DEPLOYMENT.md ("Backups").
set -euo pipefail
cd "$(dirname "$0")"

KEEP="${KEEP:-14}"

docker compose exec -T api python _scripts/backup_analytics.py --out-dir /data/backups --keep "$KEEP"
mkdir -p backups
docker compose cp api:/data/backups/. ./backups/

# keep only the newest KEEP files on the host as well
ls -1t backups/analytics-*.db.gz 2>/dev/null | tail -n +"$((KEEP + 1))" | while read -r old; do rm -f "$old"; done
echo "Backups in ./backups: $(ls -1 backups/analytics-*.db.gz 2>/dev/null | wc -l) (newest: $(ls -1t backups/analytics-*.db.gz | head -1))"
