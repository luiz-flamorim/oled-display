from luma.core.interface.serial import spi
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import time


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
    font_size = 12
    font = ImageFont.truetype(font_path, font_size)

    width, height = device.width, device.height
    image = Image.new("1", (width, height))
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    lines = wrap_text(message, font, width, draw)
    line_height = font.getbbox("A")[3] + 2
    total_height = line_height * len(lines)

    if total_height <= height:
        # No need to scroll — just show it
        y = 0
        for line in lines:
            draw.text((0, y), line, font=font, fill=255)
            y += line_height
        device.display(image)
        time.sleep(5)
    else:
        # Need to scroll vertically
        scroll_image = Image.new("1", (width, total_height))
        scroll_draw = ImageDraw.Draw(scroll_image)

        y = 0
        for line in lines:
            scroll_draw.text((0, y), line, font=font, fill=255)
            y += line_height

        # Animate scroll
        for offset in range(0, total_height - height + 1):
            frame = scroll_image.crop((0, offset, width, offset + height))
            device.display(frame)
            time.sleep(0.03)

        time.sleep(2)  # Pause at the end of the scroll
