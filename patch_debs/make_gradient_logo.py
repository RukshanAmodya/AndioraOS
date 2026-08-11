import os, re
from PIL import Image, ImageDraw, ImageFont

with open('f:/Projects/AnduinOS-2/logo.svg', 'r', encoding='utf-8') as f:
    svg = f.read()

paths = re.findall(r'd="([^"]+)"', svg)

parsed_paths = []
for p in paths:
    coords = re.findall(r'([0-9.]+),([0-9.]+)', p)
    pts = [(float(x), float(y)) for x, y in coords]
    if len(pts) > 2:
        parsed_paths.append(pts)

print(f"Parsed {len(parsed_paths)} valid polygon paths from logo.svg")

# High-res canvas 1254x1254
canvas = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))

# Left Gradient: Red top (#ff3f3f) -> Purple middle (#9b6bd3) -> Blue bottom (#0878f5)
mask_left = Image.new('L', (1254, 1254), 0)
ImageDraw.Draw(mask_left).polygon(parsed_paths[0], fill=255)

grad_left = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))
for y in range(1254):
    t = y / 1254.0
    if t < 0.5:
        f = t * 2.0
        r = int(255 * (1 - f) + 155 * f)
        g = int(63 * (1 - f) + 107 * f)
        b = int(63 * (1 - f) + 211 * f)
    else:
        f = (t - 0.5) * 2.0
        r = int(155 * (1 - f) + 8 * f)
        g = int(107 * (1 - f) + 120 * f)
        b = int(211 * (1 - f) + 245 * f)
    ImageDraw.Draw(grad_left).line([(0, y), (1254, y)], fill=(r, g, b, 255))

canvas.paste(grad_left, (0, 0), mask_left)

# Right Gradient: Green top (#05c85a) -> Yellow middle (#d7d800) -> Orange bottom (#ffc20a)
mask_right = Image.new('L', (1254, 1254), 0)
ImageDraw.Draw(mask_right).polygon(parsed_paths[1], fill=255)

grad_right = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))
for y in range(1254):
    t = y / 1254.0
    if t < 0.5:
        f = t * 2.0
        r = int(5 * (1 - f) + 215 * f)
        g = int(200 * (1 - f) + 216 * f)
        b = int(90 * (1 - f) + 0 * f)
    else:
        f = (t - 0.5) * 2.0
        r = int(215 * (1 - f) + 255 * f)
        g = int(216 * (1 - f) + 194 * f)
        b = int(0 * (1 - f) + 10 * f)
    ImageDraw.Draw(grad_right).line([(0, y), (1254, y)], fill=(r, g, b, 255))

canvas.paste(grad_right, (0, 0), mask_right)

canvas.save('f:/Projects/AnduinOS-2/patch_debs/full_gradient_logo.png')
print("Rendered full 1254x1254 multi-color gradient logo icon!")

# 1. Create Plymouth Center Boot Splash Logo (logo_96.png & bgrt-fallback.png - 96x96 & 160x160)
# Get bounding box to perfectly center the logo
bbox = canvas.getbbox()
icon_cropped = canvas.crop(bbox)

# Create 160x160 perfectly centered boot splash icon
boot_center = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
scale_c = 136 / max(icon_cropped.size)
icon_scaled_c = icon_cropped.resize((int(icon_cropped.size[0] * scale_c), int(icon_cropped.size[1] * scale_c)), Image.LANCZOS)
px = (160 - icon_scaled_c.size[0]) // 2
py = (160 - icon_scaled_c.size[1]) // 2
boot_center.paste(icon_scaled_c, (px, py), icon_scaled_c)

boot_center.save('f:/Projects/AnduinOS-2/patch_debs/bgrt-fallback.png')
boot_center.resize((96, 96), Image.LANCZOS).save('f:/Projects/AnduinOS-2/patch_debs/logo_96.png')
print("Saved centered boot splash icons: bgrt-fallback.png & logo_96.png")

# 2. Create Watermark Logo (300x61) with full gradient icon + ANDIORA text
watermark = Image.new('RGBA', (300, 61), (0, 0, 0, 0))
scale_wm = 48 / icon_cropped.size[1]
icon_wm = icon_cropped.resize((int(icon_cropped.size[0] * scale_wm), 48), Image.LANCZOS)
watermark.paste(icon_wm, (10, 6), icon_wm)

w_draw = ImageDraw.Draw(watermark)
try:
    font = ImageFont.truetype("arialbd.ttf", 30)
except:
    font = ImageFont.load_default()

w_draw.text((68, 12), "ANDIORA", fill=(255, 255, 255, 255), font=font)
watermark.save('f:/Projects/AnduinOS-2/patch_debs/andiora_watermark.png')
print("Saved andiora_watermark.png (300x61) with multi-color gradient logo!")
