#!/bin/bash
# SnapDB creation script - run via crontab every 5 minutes
# IMPORTANT: Stop the harmony service BEFORE enabling this crontab
# Example crontab entry (use absolute paths):
#   */5 * * * * /bin/bash /home/serviceharmony/harmony-toolbox/src/bin/check-and-run-snapdb.sh

HARMONY_DIR="$HOME/harmony0"
BINARY="$HARMONY_DIR/harmony"
DB_PATH="$HARMONY_DIR/harmony_db_0"
SNAPDB_PATH="$HARMONY_DIR/new_snapdb_creation"
LOG_FILE="$HARMONY_DIR/newsnapdb.log"

# Make sure the destination folder exists
mkdir -p "$SNAPDB_PATH"

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check if dumpdb is already running (not the harmony service, the dump process)
if pgrep -f "harmony dumpdb" > /dev/null 2>&1; then
    echo "[$TIMESTAMP] dumpdb already running, skipping." | tee -a "$LOG_FILE"
    exit 0
fi

# Warn if harmony service is still active
if systemctl is-active --quiet harmony0; then
    echo "[$TIMESTAMP] ERROR: harmony0 service is still running. Stop it first with: sudo service harmony0 stop" | tee -a "$LOG_FILE"
    exit 1
fi

echo "[$TIMESTAMP] Starting dumpdb: $DB_PATH -> $SNAPDB_PATH" | tee -a "$LOG_FILE"

"$BINARY" dumpdb "$DB_PATH" "$SNAPDB_PATH" 2>&1 | \
    grep -v "KakashiDB batch writhing\|account" | \
    tee -a "$LOG_FILE" &

echo "[$TIMESTAMP] dumpdb started in background. Monitor progress with: tail -f $LOG_FILE"
