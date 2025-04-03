from bs4 import BeautifulSoup
import requests

def extract_headlines(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    candidates = []

    # 1. Try headline tags
    for tag in ['h1', 'h2', 'h3', 'article', 'header']:
        candidates.extend(soup.find_all(tag))

    # 2. Try known headline classes
    for class_name in ['headline', 'entry-title', 'title', 'post-title', 'gs-c-promo-heading__title']:
        candidates.extend(soup.find_all(class_=class_name))

    # 3. Extract and clean text
    seen = set()
    headlines = []
    for c in candidates:
        text = c.get_text(strip=True)
        if text and text not in seen:
            seen.add(text)
            headlines.append(text)

    return headlines[:10]  # You can increase this if you like

headlines = extract_headlines("https://www.bbc.com/news")
for line in headlines:
    print(line)
