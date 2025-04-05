# Scrape and Display

This app is designed to continuously scrape headlines from global news sources and render them in real-time on a SH1106 OLED screen via SPI. The display cycles through headlines in various languages, managing text wrapping and scroll animation where necessary. It also includes a dynamic system HUD showing uptime, RAM, CPU usage, and SD card usage, providing a visual representation of system performance and load.

## Functionality Breakdown

### `main.py`
- Entry point of the application.
- Launches a separate thread to log system metrics to a local file (`ping_log.txt`) at 1-second intervals.
- Iterates through a list of multilingual news sources, scrapes headlines, and passes the result to the OLED renderer.
- Displays a temporary "scraping in progress" screen before fetching each source.
- Continuously loops over the collected headlines, rendering them to screen indefinitely.

### `scraper.py`
- Uses `requests` and `BeautifulSoup` to fetch and parse HTML pages.
- Searches for headlines by tag (`h1`, `h2`, `h3`) and by common CSS class names related to headlines.
- Applies basic filters to discard overly long text or complete paragraphs.
- Returns a list of cleaned strings for display.

### `oled_display.py`
- Controls the SH1106 OLED display via the `luma.oled` library.
- Loads language-specific fonts from local `fonts/` directory using PIL.
- Wraps text to fit within the 128x64 pixel screen bounds.
- Draws a persistent HUD at the top with system uptime, RAM, CPU, and SD card usage.
- Displays all headlines either directly (if space allows) or with a vertical scroll effect.
- Also includes a placeholder "scraping" message to be shown during fetching operations.

### `ping_logger.py`
- Appends a new line with CPU and RAM usage every second to `ping_log.txt`.
- Resets the log file on first run.

## Required Libraries

Ensure the following Python packages are installed:

```bash
pip install luma.oled pillow psutil requests beautifulsoup4
```

Additional system-level packages may be required:

```bash
sudo apt install ttf-dejavu fonts-noto
```

## Hardware Requirements

- Raspberry Pi (tested on Pi Zero 2W)
- SH1106 OLED screen (connected via SPI)
- Fonts directory containing Noto fonts for multiple languages

## File Structure

```
Project/
│
├── main.py
├── scraper.py
├── ping_logger.py
├── oled_display.py
├── ping_log.txt
├── fonts/
│   ├── NotoSans-Regular.ttf
│   ├── NotoSans-C-Regular.ttf
│   ├── NotoSansDevanagari-Regular.ttf
│   ├── ...
```

## Fonts

This project supports multiple scripts and uses a specific font for each language to ensure proper rendering. Fonts are loaded from the `fonts/` directory. Ensure the following fonts are present:
- NotoSans-Regular.ttf,
- NotoSans-C-Regular.ttf,
- NotoSansDevanagari-Regular.ttf,
- NotoSansMalayalam-Regular.ttf,
- NotoSans-Regular.ttf,
- NotoSans-Regular.ttf,
- NotoSans-C-Regular.ttf,
- NotoSansCJKjp-Regular.otf,
- NotoSansCJK-Regular.ttc,
- NotoSansCJK-Regular.ttc

## Running the App

Once everything is set up and wired correctly:

```bash
python3 main.py
```

The system will begin logging system metrics, scrape multilingual headlines, and start rendering them on the OLED display with performance indicators.

## Notes

- If any fonts are missing, a warning will be printed at startup.
- The HUD bar uses RAM percentage to generate a dynamic visual bar, emulating system saturation.
- Headlines are displayed in a shuffled order to simulate information overload.
