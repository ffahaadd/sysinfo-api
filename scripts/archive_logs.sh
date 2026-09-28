#!/bin/bash

# ─────────────────────────────────────────────────────────────
# archive_logs.sh
# Archives the Nginx access log for sysinfo-api weekly.
# Designed to run via crontab (as root).
# ─────────────────────────────────────────────────────────────

LOG_FILE="/var/log/nginx/sysinfo-api.access.log"
ARCHIVE_DIR="/var/log/nginx/archives"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
ARCHIVED_FILE="${ARCHIVE_DIR}/access_${TIMESTAMP}.log.gz"

# Create archive directory if it doesn't exist
mkdir -p "$ARCHIVE_DIR"

# Check if log file exists and is non-empty
if [[ ! -s "$LOG_FILE" ]]; then
    echo "$(date): Log file is empty or missing. Skipping." \
        | tee -a /var/log/archive_logs.log
    exit 0
fi

# Compress and archive
gzip -c "$LOG_FILE" > "$ARCHIVED_FILE"

if [[ $? -eq 0 ]]; then
    # Clear the original log
    > "$LOG_FILE"

    echo "$(date): Archived to $ARCHIVED_FILE" \
        | tee -a /var/log/archive_logs.log
else
    echo "$(date): ERROR - archiving failed." \
        | tee -a /var/log/archive_logs.log
    exit 1
fi

# Remove archives older than 30 days
find "$ARCHIVE_DIR" -name "*.log.gz" -mtime +30 -delete
echo "$(date): Cleanup complete." \
    | tee -a /var/log/archive_logs.log
