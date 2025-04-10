#!/bin/bash

LOGFILE="/home/luizamorim/oled_project/logs/boot_log.txt"
MAX_LINES=300

trim_log_file() {
    if [ -f "$LOGFILE" ]; then
        lines=$(wc -l < "$LOGFILE")
        if [ "$lines" -gt "$MAX_LINES" ]; then
            tail -n "$MAX_LINES" "$LOGFILE" > "${LOGFILE}.tmp" && mv "${LOGFILE}.tmp" "$LOGFILE"
            echo "[log] Trimmed to last $MAX_LINES lines." >> $LOGFILE
        fi
    fi
}

trim_service_log_file() {
    local logfile=$1
    local max_lines=500

    if [ -f "$logfile" ]; then
        local lines
        lines=$(wc -l < "$logfile")
        if [ "$lines" -gt "$max_lines" ]; then
            tail -n "$max_lines" "$logfile" > "${logfile}.tmp" && mv "${logfile}.tmp" "$logfile"
            echo "[log] Trimmed: $logfile to last $max_lines lines."
        fi
    fi
}

echo "=== Thanatos boot start === $(date)" >> $LOGFILE
echo "Waiting for network..." >> $LOGFILE

for i in {1..30}; do
    if ping -c 1 google.com &> /dev/null; then
        echo "Network is up. Starting Thanatos..." >> $LOGFILE
        break
    fi
    sleep 1
done

if ! ping -c 1 google.com &> /dev/null; then
    echo "No network detected. Aborting Thanatos launch." >> $LOGFILE
    trim_log_file
    exit 1
fi

echo "Activating virtualenv and launching..." >> $LOGFILE
source /home/luizamorim/oled_project/venv/bin/activate

# Clear old nohup log and launch the script
> /home/luizamorim/oled_project/logs/nohup.out
nohup python3 /home/luizamorim/oled_project/main.py > /home/luizamorim/oled_project/logs/nohup.out 2>&1 &

echo "Thanatos launched." >> $LOGFILE
trim_log_file