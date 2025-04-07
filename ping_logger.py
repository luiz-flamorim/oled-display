from datetime import datetime
import psutil
import os

LOG_FILE = "logs/ping_log.txt"
MAX_LINES = 500
first_ping = True

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_system_stats():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/')
    disk_free_gb = round(disk.free / (1024 ** 3), 2)   # GB
    disk_percent = disk.percent
    return cpu, ram, disk_free_gb, disk_percent

def trim_log_file():
    if not os.path.exists(LOG_FILE):
        return

    with open(LOG_FILE, "r") as file:
        lines = file.readlines()

    if len(lines) > MAX_LINES:
        # Keep only the most recent N lines
        with open(LOG_FILE, "w") as file:
            file.writelines(lines[-MAX_LINES:])
        print(f"[log] Trimmed to last {MAX_LINES} lines.")

def log_ping():
    global first_ping
    timestamp = get_timestamp()
    cpu, ram, disk_free_gb, disk_percent = get_system_stats()

    line = (
        f"{timestamp}\t"
        f"CPU: {cpu}%\t"
        f"RAM: {ram}%\t"
        f"Disk Free: {disk_free_gb}GB ({100 - disk_percent}%)\n"
    )

    mode = "w" if first_ping else "a"

    with open(LOG_FILE, mode) as file:
        file.write(line)

    if first_ping:
        print(f"[log] Ping log started: {line.strip()}")
        first_ping = False

    trim_log_file()
