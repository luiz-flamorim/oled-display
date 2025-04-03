from luma.core.interface.serial import spi
from luma.oled.device import sh1106
from PIL import Image, ImageDraw, ImageFont
import textwrap
import time

# Match your exact wiring: DC=25, RST=27, CS=CE0 (device=0)
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

# display image
def display_message(message):
    image = Image.new("1", (device.width, device.height))
    draw = ImageDraw.Draw(image)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, 12)

    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)

    lines = wrap_text(message, font, device.width, draw)

    y = 0
    for line in lines:
        draw.text((0, y), line, font=font, fill=255)
        y += font.getbbox(line)[3] + 2  # height + spacing

    device.display(image)

# Example usage
if __name__ == "__main__":
    print("Displaying message...")
    display_message("Test")
    time.sleep(10)
    display_message("")
