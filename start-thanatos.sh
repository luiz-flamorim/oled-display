#!/bin/bash

LOGFILE="/home/luizamorim/oled_project/bootlog.txt"

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
    exit 1
fi

echo "Activating virtualenv and launching..." >> $LOGFILE
source /home/luizamorim/oled_project/venv/bin/activate
> /home/luizamorim/oled_project/nohup.out
nohup python3 /home/luizamorim/oled_project/main.py > /home/luizamorim/oled_project/nohup.out 2>&1 &
echo "Thanatos launched." >> $LOGFILE
