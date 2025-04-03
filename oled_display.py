from luma.core.interface.serial import spi
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import time
import shutil
import psutil

# usage information
def get_sd_usage_percent():
    total, used, free = shutil.disk_usage("/")
    percent = int(used / total * 100)
    return percent

def get_uptime_minutes():
    uptime_seconds = int(time.time() - psutil.boot_time())
    return uptime_seconds // 60

# Setup display
serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27)
device = sh1106(serial)

def wrap_text(message, font, max_width, draw):
    lines = []
    for paragraph in message.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            if text_width <= max_width:
                line = test_line
            else:
                lines.append(line.strip())
                line = word + " "
        if line:
            lines.append(line.strip())
    return lines

def display_message(message):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 10)
    hud_font = ImageFont.truetype(font_path, 8)  # smaller font for HUD

    width, height = device.width, device.height
    hud_height = 25  # smaller now that font is smaller

    linespace = font.getbbox("A")[3] + 2

    # Wrap text
    temp_image = Image.new("1", (width, height))
    temp_draw = ImageDraw.Draw(temp_image)
    lines = wrap_text(message, font, width, temp_draw)
    line_height = linespace
    total_height = line_height * len(lines)

    if total_height <= (height - hud_height):
        # Static message (no scroll needed)
        image = Image.new("1", (width, height))
        draw = ImageDraw.Draw(image)

        # HUD background
        draw.rectangle((0, 0, width, hud_height), outline=0, fill=0)

        # HUD content
        uptime = get_uptime_minutes()
        ram = int(psutil.virtual_memory().percent)
        cpu = int(psutil.cpu_percent())
        up_str = f"{uptime}min" if uptime < 60 else f"{uptime // 60}h"

        # Line 1
        sys_info = f"UP {up_str} | RAM {ram}% | CPU {cpu}%"
        draw.text((1, 0), sys_info, font=hud_font, fill=255)

        # Line 2
        sd_percent = get_sd_usage_percent()
        progress_bar = "[" + "█" * 10 + "]"  # fully filled since no scrolling
        draw.text((1, 10), f"SD {sd_percent}% {progress_bar}", font=hud_font, fill=255)

        # Message
        y = hud_height
        for line in lines:
            draw.text((0, y), line, font=font, fill=255)
            y += line_height

        device.display(image)
        time.sleep(5)

    else:
        # Scroll needed
        scroll_image = Image.new("1", (width, total_height))
        scroll_draw = ImageDraw.Draw(scroll_image)

        y = 0
        for line in lines:
            scroll_draw.text((0, y), line, font=font, fill=255)
            y += line_height

        for offset in range(0, total_height - (height - hud_height) + 1):
            frame = Image.new("1", (width, height))
            draw = ImageDraw.Draw(frame)

            # HUD background
            draw.rectangle((0, 0, width, hud_height), outline=0, fill=0)

            # HUD info
            uptime = get_uptime_minutes()
            ram = int(psutil.virtual_memory().percent)
            cpu = int(psutil.cpu_percent())
            up_str = f"{uptime}min" if uptime < 60 else f"{uptime // 60}h"

            sys_info = f"UP {up_str} | RAM {ram}% | CPU {cpu}%"
            draw.text((1, 0), sys_info, font=hud_font, fill=255)

            sd_percent = get_sd_usage_percent()
            progress_ratio = (offset + height) / total_height
            blocks_total = 10
            filled_blocks = int(progress_ratio * blocks_total)
            bar = "[" + "█" * filled_blocks + "░" * (blocks_total - filled_blocks) + "]"

            draw.text((1, 10), f"SD {sd_percent}% {bar}", font=hud_font, fill=255)

            # Scrollable message
            visible_part = scroll_image.crop((0, offset, width, offset + height - hud_height))
            frame.paste(visible_part, (0, hud_height))

            device.display(frame)
            time.sleep(0.03)

        time.sleep(2)
