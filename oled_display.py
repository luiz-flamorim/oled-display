from luma.core.interface.serial import spi
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import time
import shutil
import psutil
import os

# So main.py can use this new function
__all__ = ["display_message", "display_scraping_message"]

# Font path map by language
FONT_PATHS = {
    "en": "fonts/NotoSans-Regular.ttf",
    "ru": "fonts/NotoSans-C-Regular.ttf",
    "hi": "fonts/NotoSansDevanagari-Regular.ttf",
    # "ml": "fonts/NotoSansMalayalam-Regular.ttf",
    "pt": "fonts/NotoSans-Regular.ttf",
    "fr": "fonts/NotoSans-Regular.ttf",
    "uk": "fonts/NotoSans-C-Regular.ttf",
    "ja": "fonts/NotoSansCJKjp-Regular.otf",
    "zh": "fonts/NotoSansCJK-Regular.ttc",
    "ko": "fonts/NotoSansCJK-Regular.ttc",
}

# Validate font paths
for lang, path in FONT_PATHS.items():
    if not os.path.exists(path):
        print(f"[!] Missing font for '{lang}': {path}")

# Load all fonts once
LOADED_FONTS = {lang: ImageFont.truetype(path, 10) for lang, path in FONT_PATHS.items() if os.path.exists(path)}

# HUD font (separate and smaller)
HUD_FONT_PATH = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
hud_font = ImageFont.truetype(HUD_FONT_PATH, 8)

# Display setup
serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27)
device = sh1106(serial)

# System info
def get_sd_usage_percent():
    total, used, free = shutil.disk_usage("/")
    return int(used / total * 100)

def get_uptime_minutes():
    uptime_seconds = int(time.time() - psutil.boot_time())
    return uptime_seconds // 60

# Wrap text to fit screen
def wrap_text(line, font, max_width, draw):
    wrapped = []
    words = line.split()
    line_buf = ""
    for word in words:
        test_line = line_buf + word + " "
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width:
            line_buf = test_line
        else:
            wrapped.append(line_buf.strip())
            line_buf = word + " "
    if line_buf:
        wrapped.append(line_buf.strip())
    return wrapped

def display_message(headlines):
    width, height = device.width, device.height
    hud_height = 25

    # Temporary canvas for measuring
    temp_image = Image.new("1", (width, height))
    temp_draw = ImageDraw.Draw(temp_image)

    display_lines = []
    line_height = 0

    for item in headlines:
        lang = item.get("lang", "en")
        text = item.get("text", "")
        font = LOADED_FONTS.get(lang, LOADED_FONTS["en"])

        lines = wrap_text(text, font, width, temp_draw)
        for l in lines:
            display_lines.append({ "text": l, "font": font })
            if line_height == 0:
                line_height = font.getbbox("A")[3] + 2

    total_height = line_height * len(display_lines)

    def draw_hud(draw):
        uptime = get_uptime_minutes()
        ram = int(psutil.virtual_memory().percent)
        cpu = int(psutil.cpu_percent())
        up_str = f"{uptime}min" if uptime < 60 else f"{uptime // 60}h"
        sys_info = f"UP {up_str} | RAM {ram}% | CPU {cpu}%"
        draw.text((1, 0), sys_info, font=hud_font, fill=255)

        sd_percent = get_sd_usage_percent()
        bar_blocks = 40
        filled = int(ram / 100 * bar_blocks)
        bar = "[" + ":".join([""] * filled) + "." * (bar_blocks - filled) + "]"
        draw.text((1, 10), f"SD {sd_percent}% {bar}", font=hud_font, fill=255)

    if total_height <= (height - hud_height):
        image = Image.new("1", (width, height))
        draw = ImageDraw.Draw(image)

        draw.rectangle((0, 0, width, hud_height), fill=0)
        draw_hud(draw)

        y = hud_height
        for line in display_lines:
            draw.text((0, y), line["text"], font=line["font"], fill=255)
            y += line_height

        device.display(image)
        time.sleep(5)

    else:
        scroll_image = Image.new("1", (width, total_height))
        scroll_draw = ImageDraw.Draw(scroll_image)

        y = 0
        for line in display_lines:
            scroll_draw.text((0, y), line["text"], font=line["font"], fill=255)
            y += line_height

        for offset in range(0, total_height - (height - hud_height) + 1):
            frame = Image.new("1", (width, height))
            draw = ImageDraw.Draw(frame)

            draw.rectangle((0, 0, width, hud_height), fill=0)
            draw_hud(draw)

            visible_part = scroll_image.crop((0, offset, width, offset + height - hud_height))
            frame.paste(visible_part, (0, hud_height))

            device.display(frame)
            time.sleep(0.03)

        time.sleep(2)


def display_scraping_message():
    width, height = device.width, device.height

    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)

    # HUD background
    draw.rectangle((0, 0, width, 25), fill=0)

    # System info
    uptime = get_uptime_minutes()
    ram = int(psutil.virtual_memory().percent)
    cpu = int(psutil.cpu_percent())
    up_str = f"{uptime}min" if uptime < 60 else f"{uptime // 60}h"
    sys_info = f"UP {up_str} | RAM {ram}% | CPU {cpu}%"
    draw.text((1, 0), sys_info, font=hud_font, fill=255)

    # SD usage and RAM-based bar
    sd_percent = get_sd_usage_percent()

    bar_blocks = 40
    filled = int(ram / 100 * bar_blocks)
    bar = "[" + ":".join([""] * filled) + "." * (bar_blocks - filled) + "]"

    draw.text((1, 10), f"SD {sd_percent}% {bar}", font=hud_font, fill=255)

    # Scraping message
    message = "::: ##### :::"
    font = LOADED_FONTS["en"]
    bbox = draw.textbbox((0, 0), message, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2 + 10

    draw.text((x, y), message, font=font, fill=255)

    device.display(image)
