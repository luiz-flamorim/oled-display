from datetime import datetime
import psutil

LOG_FILE = "ping_log.txt"
first_ping = True

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_system_stats():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return cpu, ram

def log_ping():
    global first_ping
    timestamp = get_timestamp()
    cpu, ram = get_system_stats()

    line = f"{timestamp}\tCPU: {cpu}%\tRAM: {ram}%\n"
    mode = "w" if first_ping else "a"

    with open(LOG_FILE, mode) as file:
        file.write(line)

    if first_ping:
        print(f"Ping log started: {line.strip()}")
        first_ping = False
