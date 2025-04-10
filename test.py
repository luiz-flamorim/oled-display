import os
from PIL import Image, ImageDraw, ImageFont, features

print("Raqm support:", features.check('raqm'))
print("RAQM:", features.check("raqm"))
print("HarfBuzz:", features.check("harfbuzz"))
print("FriBidi:", features.check("fribidi"))

# Layout engine fallback
LAYOUT_BASIC = getattr(ImageFont, "LAYOUT_BASIC", 0)
LAYOUT_RAQM = getattr(ImageFont, "LAYOUT_RAQM", 0)
LAYOUT_ENGINE = LAYOUT_RAQM if features.check("raqm") else LAYOUT_BASIC

font_path = "fonts/NotoSansDevanagari-Regular.ttf"

if not os.path.exists(font_path):
    print(f"[!] Missing font: {font_path}")
else:
    font = ImageFont.truetype(font_path, 16, layout_engine=LAYOUT_ENGINE)

    img = Image.new("L", (128, 64), 255)  # Greyscale image
    draw = ImageDraw.Draw(img)

    draw.text((10, 10), "नमस्ते", font=font, fill=0)
    img.save("test_devanagari.png")
    print("✅ Saved test_devanagari.png")
