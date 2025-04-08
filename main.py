import random
import time
import threading
import json
from datetime import datetime
from pathlib import Path
from scraper import extract_headlines, save_headlines, sources
from oled_display import display_message, display_scraping_message
from ping_logger import log_ping

PING_INTERVAL = 1  # seconds
SCRAPE_INTERVAL = 1800  # 30 minutes in seconds
LOG_PATH = Path("logs/main_log.txt")
MAX_LOG_LINES = 500

def log_main_event(message):
    Path("logs").mkdir(exist_ok=True)
    timestamp = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    log_line = f"[{timestamp}] {message}\n"

    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(log_line)

    with open(LOG_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) > MAX_LOG_LINES:
        with open(LOG_PATH, 'w', encoding='utf-8') as f:
            f.writelines(lines[-MAX_LOG_LINES:])

def ping_loop():
    while True:
        log_ping()
        time.sleep(PING_INTERVAL)

def load_headlines():
    today_file = Path(f"news/{datetime.utcnow().strftime('%Y-%m-%d')}.json")
    all_headlines = []

    if today_file.exists():
        with open(today_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for source_data in data.get(today_file.stem, {}).values():
            for h in source_data.get("headlines", []):
                all_headlines.append({ "text": h["text"], "lang": "en" })  # default to "en"
    else:
        log_main_event("[WARN] No news file found.")

    return all_headlines

def scrape_random_source():
    source = random.choice(sources)
    log_main_event(f"[{source['name']}] Triggering background scrape...")
    headlines = extract_headlines(source["url"])
    if headlines:
        save_headlines(source["name"], headlines)
    else:
        log_main_event(f"[{source['name']}] No headlines found")

def main():
    display_scraping_message()
    
    ping_thread = threading.Thread(target=ping_loop, daemon=True)
    ping_thread.start()

    all_headlines = load_headlines()
    if not all_headlines:
        log_main_event("[INIT] No headlines found, running startup scrape...")
        display_scraping_message()
        scrape_random_source()
        all_headlines = load_headlines()

        if not all_headlines:
            log_main_event("[INIT] Still no headlines after scrape.")
            all_headlines = [{ "text": "Thanatos found no news.", "lang": "en" }]


    random.shuffle(all_headlines)
    last_scrape_time = time.time()

    try:
        while True:
            display_message(all_headlines)

            now = time.time()
            if now - last_scrape_time >= SCRAPE_INTERVAL:
                log_main_event("[MAIN] Running periodic scrape...")
                display_scraping_message()
                scrape_random_source()
                all_headlines = load_headlines()
                random.shuffle(all_headlines)
                last_scrape_time = now

    except Exception as e:
        log_main_event(f"[ERROR] Thanatos crashed: {e}")
        display_message([{ "text": "Thanatos failed. Check logs.", "lang": "en" }])

if __name__ == "__main__":
    main()
