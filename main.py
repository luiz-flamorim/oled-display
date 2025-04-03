from scraper import extract_headlines
from oled_display import display_message
import time

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

    separator = " ::: " 
    combined = separator.join(all_headlines)

    print("Displaying combined headlines...")
    display_message(combined)

if __name__ == "__main__":
    main()
