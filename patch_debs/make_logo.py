from PIL import Image, ImageDraw, ImageFont
import re

with open('f:/Projects/AnduinOS-2/logo.svg', 'r', encoding='utf-8') as f:
    svg = f.read()

paths = re.findall(r'd="([^"]+)"', svg)
print(f"Found {len(paths)} paths in logo.svg")

parsed_paths = []
all_pts = []
for p in paths:
    coords = re.findall(r'([0-9.]+),([0-9.]+)', p)
    pts = [(float(x), float(y)) for x, y in coords]
    if pts:
        parsed_paths.append(pts)
        all_pts.extend(pts)

# Draw SVG icon at hi-res (1254x1254)
canvas = Image.new('RGBA', (1254, 1254), (0, 0, 0, 0))
draw = ImageDraw.Draw(canvas)

# Fill left shape (Red-Blue gradient) & right shape (Green-Yellow gradient)
if len(parsed_paths) >= 2:
    draw.polygon(parsed_paths[0], fill=(220, 60, 90, 255))
    draw.polygon(parsed_paths[1], fill=(40, 190, 100, 255))

canvas.save('f:/Projects/AnduinOS-2/patch_debs/new_logo_icon.png')
print("Saved new_logo_icon.png")

# Now create composite Watermark Logo (300x61) with icon on left + 'ANDIORA' text on right
watermark = Image.new('RGBA', (300, 61), (0, 0, 0, 0))

# Scale icon to height 48px
scale = 48 / 1254
icon_resized = canvas.resize((int(1254 * scale), 48), Image.LANCZOS)
watermark.paste(icon_resized, (8, 6), icon_resized)

# Draw ANDIORA text in bold white
w_draw = ImageDraw.Draw(watermark)
try:
    font = ImageFont.truetype("arialbd.ttf", 32)
except:
    font = ImageFont.load_default()

w_draw.text((68, 11), "ANDIORA", fill=(255, 255, 255, 255), font=font)

watermark.save('f:/Projects/AnduinOS-2/patch_debs/andiora_watermark.png')
print("Updated andiora_watermark.png (300x61) with user's logo.svg icon + ANDIORA text!")
