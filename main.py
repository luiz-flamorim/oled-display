from scraper import extract_headlines
from oled_display import display_message
import time

def main():
    url = "https://www.bbc.com/news"
    headlines = extract_headlines(url)

    for headline in headlines:
        print(f"Showing: {headline}")
        display_message(headline)
        time.sleep(5)

if __name__ == "__main__":
    main()
