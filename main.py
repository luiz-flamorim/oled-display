import random
import time
import threading
from scraper import extract_headlines
from oled_display import display_message, display_scraping_message
from ping_logger import log_ping

PING_INTERVAL = 1  # seconds

def ping_loop():
    """Continuously log a ping in the background."""
    while True:
        log_ping()
        time.sleep(PING_INTERVAL)

def main():
    # Start ping logger thread
    ping_thread = threading.Thread(target=ping_loop, daemon=True)
    ping_thread.start()

    # Your original code
    sources = [
        { "lang": "en", "url": "https://www.bbc.com/news" },
        { "lang": "en", "url": "https://www.theguardian.com/international" },
        { "lang": "en", "url": "https://www.reuters.com/" },
        { "lang": "ja", "url": "https://www3.nhk.or.jp/news/" },
        { "lang": "ja", "url": "https://www.asahi.com/" },
        { "lang": "zh", "url": "http://paper.people.com.cn/" },
        { "lang": "zh", "url": "https://news.sina.com.cn/" },
        { "lang": "ru", "url": "https://russian.rt.com/" },
        { "lang": "ru", "url": "https://www.rbc.ru/" },
        { "lang": "hi", "url": "https://www.bhaskar.com/" },
        { "lang": "ml", "url": "https://www.manoramaonline.com/" },
        { "lang": "pt", "url": "https://g1.globo.com/" },
        { "lang": "fr", "url": "https://www.lemonde.fr/" },
        { "lang": "uk", "url": "https://www.pravda.com.ua/" },
        { "lang": "ko", "url": "https://www.yna.co.kr/" }
    ]

    all_headlines = []

    for source in sources:
        display_scraping_message()
        lang = source["lang"]
        url = source["url"]
        print(f"Scraping {url}...")
        headlines = extract_headlines(url)
        for h in headlines:
            all_headlines.append({ "text": h, "lang": lang })

    # Shuffle headlines to simulate overload
    random.shuffle(all_headlines)

    # Infinite loop
    while True:
        display_message(all_headlines)

if __name__ == "__main__":
    main()
