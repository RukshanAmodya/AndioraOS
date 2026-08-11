import os, re
from PIL import Image, ImageDraw, ImageFont

# Read SVG
with open('f:/Projects/AnduinOS-2/logo.svg', 'r', encoding='utf-8') as f:
    svg = f.read()

paths = re.findall(r'd="([^"]+)"', svg)

def get_pts(path_str):
    coords = re.findall(r'([0-9.]+),([0-9.]+)', path_str)
    return [(float(x), float(y)) for x, y in coords]

path_left = get_pts(paths[0])
path_right = get_pts(paths[1])

# High-res canvas 1254x1254
canvas = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))

# Left Gradient: Red -> Purple -> Blue
# Create mask for left path
mask_left = Image.new('L', (1254, 1254), 0)
ImageDraw.Draw(mask_left).polygon(path_left, fill=255)

# Create left gradient fill (Vertical/Diagonal: Red top-left #ff3f3f -> Purple middle #9b6bd3 -> Blue bottom #0878f5)
grad_left = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))
for y in range(1254):
    t = y / 1254.0
    if t < 0.5:
        # Red to Purple
        f = t * 2.0
        r = int(255 * (1 - f) + 155 * f)
        g = int(63 * (1 - f) + 107 * f)
        b = int(63 * (1 - f) + 211 * f)
    else:
        # Purple to Blue
        f = (t - 0.5) * 2.0
        r = int(155 * (1 - f) + 8 * f)
        g = int(107 * (1 - f) + 120 * f)
        b = int(211 * (1 - f) + 245 * f)
    ImageDraw.Draw(grad_left).line([(0, y), (1254, y)], fill=(r, g, b, 255))

canvas.paste(grad_left, (0, 0), mask_left)

# Right Gradient: Green -> Yellow -> Orange (#05c85a -> #d7d800 -> #ffc20a)
mask_right = Image.new('L', (1254, 1254), 0)
ImageDraw.Draw(mask_right).polygon(path_right, fill=255)

grad_right = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))
for y in range(1254):
    t = y / 1254.0
    if t < 0.5:
        # Green to Yellow
        f = t * 2.0
        r = int(5 * (1 - f) + 215 * f)
        g = int(200 * (1 - f) + 216 * f)
        b = int(90 * (1 - f) + 0 * f)
    else:
        # Yellow to Orange
        f = (t - 0.5) * 2.0
        r = int(215 * (1 - f) + 255 * f)
        g = int(216 * (1 - f) + 194 * f)
        b = int(0 * (1 - f) + 10 * f)
    ImageDraw.Draw(grad_right).line([(0, y), (1254, y)], fill=(r, g, b, 255))

canvas.paste(grad_right, (0, 0), mask_right)

canvas.save('f:/Projects/AnduinOS-2/patch_debs/full_gradient_logo.png')
print("Rendered full 1254x1254 gradient logo icon!")

# 1. Create BGRT Fallback / Plymouth Main Center Logo (bgrt-fallback.png & logo_96.png - 96x96 / 128x128)
# Centered, perfectly cropped icon
bbox = canvas.getbbox()
icon_cropped = canvas.crop(bbox)

# Create 128x128 centered boot logo (for Plymouth center screen)
boot_center_logo = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
scale_c = 140 / max(icon_cropped.size)
icon_scaled_c = icon_cropped.resize((int(icon_cropped.size[0] * scale_c), int(icon_cropped.size[1] * scale_c)), Image.LANCZOS)
px = (160 - icon_scaled_c.size[0]) // 2
py = (160 - icon_scaled_c.size[1]) // 2
boot_center_logo.paste(icon_scaled_c, (px, py), icon_scaled_c)
boot_center_logo.save('f:/Projects/AnduinOS-2/patch_debs/bgrt-fallback.png')
print("Saved bgrt-fallback.png (160x160 centered boot logo icon)")

# 2. Create Watermark Logo (300x61) with exact gradient icon + ANDIORA text
watermark = Image.new('RGBA', (300, 61), (0, 0, 0, 0))
scale_wm = 48 / icon_cropped.size[1]
icon_wm = icon_cropped.resize((int(icon_cropped.size[0] * scale_wm), 48), Image.LANCZOS)
watermark.paste(icon_wm, (10, 6), icon_wm)

w_draw = ImageDraw.Draw(watermark)
try:
    font = ImageFont.truetype("arialbd.ttf", 30)
except:
    font = ImageFont.load_default()

# Centered text alongside icon
w_draw.text((68, 12), "ANDIORA", fill=(255, 255, 255, 255), font=font)
watermark.save('f:/Projects/AnduinOS-2/patch_debs/andiora_watermark.png')
print("Saved andiora_watermark.png with full gradient logo & white text")
