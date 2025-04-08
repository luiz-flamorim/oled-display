from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
from pathlib import Path

def ensure_folder(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def log_scraper_event(message):
    ensure_folder("logs")
    log_path = Path("logs/scraper_log.txt")
    time_str = datetime.utcnow().isoformat(timespec='seconds') + 'Z'
    log_line = f"[{time_str}] {message}\n"

    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(log_line)

    # Trim to last 500 lines
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if len(lines) > 500:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[-500:])

def ensure_news_folder():
    ensure_folder("news")

def extract_headlines(url):
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        log_scraper_event(f"[ERROR] Failed to fetch {url}: {e}")
        return []

    candidates = []

    for tag in ['h1', 'h2', 'h3']:
        candidates.extend(soup.find_all(tag))

    for class_name in [
        'headline', 'entry-title', 'title', 'post-title',
        'gs-c-promo-heading__title', 'card__title', 'card__heading',
        'main__feed__title', 'main__title',
    ]:
        candidates.extend(soup.find_all(class_=class_name))

    seen = set()
    headlines = []
    for c in candidates:
        text = c.get_text(strip=True)
        if text and text not in seen and len(text) < 150 and text.count('.') < 2:
            seen.add(text)
            headlines.append(text)

    return headlines

def save_headlines(source_name, headlines, output_path=None):
    now = datetime.utcnow()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.isoformat(timespec='seconds') + 'Z'

    ensure_news_folder()

    if output_path is None:
        output_path = f'news/{date_str}.json'

    log_scraper_event(f"[{source_name}] scraping started")

    path = Path(output_path)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    if date_str not in data:
        data[date_str] = {}

    if source_name not in data[date_str]:
        data[date_str][source_name] = {
            "last_checked": time_str,
            "headlines": []
        }

    existing_texts = {item["text"] for item in data[date_str][source_name]["headlines"]}

    new_entries = 0
    for text in headlines:
        if text not in existing_texts:
            data[date_str][source_name]["headlines"].append({
                "time": time_str,
                "text": text
            })
            new_entries += 1

    data[date_str][source_name]["last_checked"] = time_str

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    log_scraper_event(f"[{source_name}] scraping finished with {new_entries} new headlines")

sources = [
    { "name": "bbc", "lang": "en", "url": "https://www.bbc.com/news" },
    { "name": "guardian", "lang": "en", "url": "https://www.theguardian.com/international" },
    { "name": "reuters", "lang": "en", "url": "https://www.reuters.com/" },
    { "name": "nhk", "lang": "ja", "url": "https://www3.nhk.or.jp/news/" },
    { "name": "asahi", "lang": "ja", "url": "https://www.asahi.com/" },
    { "name": "peoplecn", "lang": "zh", "url": "http://paper.people.com.cn/" },
    { "name": "sina", "lang": "zh", "url": "https://news.sina.com.cn/" },
    { "name": "rt", "lang": "ru", "url": "https://russian.rt.com/" },
    { "name": "rbc", "lang": "ru", "url": "https://www.rbc.ru/" },
    { "name": "bhaskar", "lang": "hi", "url": "https://www.bhaskar.com/" },
    { "name": "manorama", "lang": "ml", "url": "https://www.manoramaonline.com/" },
    { "name": "g1", "lang": "pt", "url": "https://g1.globo.com/" },
    { "name": "lemonde", "lang": "fr", "url": "https://www.lemonde.fr/" },
    { "name": "pravda", "lang": "uk", "url": "https://www.pravda.com.ua/" },
    { "name": "yna", "lang": "ko", "url": "https://www.yna.co.kr/" }
]

def run_scraper():
    for source in sources:
        headlines = extract_headlines(source["url"])
        if headlines:
            save_headlines(source["name"], headlines)
        else:
            log_scraper_event(f"[{source['name']}] no headlines found")

if __name__ == '__main__':
    run_scraper()
