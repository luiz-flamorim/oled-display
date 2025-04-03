from scraper import extract_headlines
from oled_display import display_message

def main():
    urls = [
        "https://www.bbc.com/news",
        "https://www.theguardian.com/international",
        "https://www.reuters.com/",
    ]

    all_headlines = []
    for url in urls:
        print(f"Scraping {url}...")
        headlines = extract_headlines(url)
        all_headlines.extend(headlines)

    # Combine into one long string with a separator
    separator = " :: "
    combined = separator.join(all_headlines)

    # Infinite loop
    while True:
        display_message(combined)

if __name__ == "__main__":
    main()
