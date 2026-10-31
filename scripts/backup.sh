#!/bin/bash
# PostgreSQL backup for tg-analytics
# Run daily via cron: 0 3 * * *

BACKUP_DIR=/opt/backups/tg-analytics
mkdir -p "$BACKUP_DIR"

docker exec tg-analytics-postgres-1 pg_dump -U tganalytics tganalytics | gzip > "$BACKUP_DIR/$(date +%Y%m%d).sql.gz"

# Keep last 30 days
find "$BACKUP_DIR" -mtime +30 -delete

echo "Backup completed: $(date)"
