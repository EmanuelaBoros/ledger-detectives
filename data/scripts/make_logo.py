"""Draw logo.png (512x512). Usage: python3 -I data/scripts/make_logo.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

S = 2
W = 512 * S
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
HELV = "/System/Library/Fonts/Helvetica.ttc"
TITLE_PT, TAG_PT = 30, 15


def P(*v):
    return [x * S for x in v]


im = Image.new("RGB", (W, W))
d = ImageDraw.Draw(im)
for y in range(W):
    t = y / W
    d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip((0x1b, 0x36, 0x63), (0x0e, 0x1c, 0x38))))
# open ledger
d.polygon(P(60, 170, 256, 200, 256, 400, 60, 370), fill="#efe3c2", outline="#c9b98c")
d.polygon(P(452, 170, 256, 200, 256, 400, 452, 370), fill="#f7edd0", outline="#c9b98c")
d.line(P(256, 200, 256, 400), fill="#a8956a", width=3 * S)
for i in range(6):
    a = 222 + i * 24
    d.line(P(78, a - 34, 238, a - 8), fill="#c8b988", width=2 * S)
    d.line(P(434, a - 34, 274, a - 8), fill="#c8b988", width=2 * S)
d.polygon(P(60, 370, 256, 400, 452, 370, 452, 382, 256, 414, 60, 382), fill="#a8956a")
# coin
cx, cy, r = 330, 262, 92
d.ellipse(P(cx - r, cy - r + 8, cx + r, cy + r + 8), fill="#a8791c")
d.ellipse(P(cx - r, cy - r, cx + r, cy + r), fill="#f2c14e", outline="#d99e22", width=5 * S)
d.ellipse(P(cx - r + 16, cy - r + 16, cx + r - 16, cy + r - 16), outline="#d99e22", width=3 * S)
d.text((cx * S, (cy - 4) * S), "F", font=ImageFont.truetype(GEORGIA, 96 * S), fill="#9a6b10", anchor="mm")
# magnifying glass
lx, ly, lr = 176, 282, 78
d.line(P(lx + 55, ly + 55, lx + 128, ly + 128), fill="#5a3b1c", width=24 * S)
d.line(P(lx + 55, ly + 55, lx + 128, ly + 128), fill="#8a5a2b", width=14 * S)
d.ellipse(P(lx - lr, ly - lr, lx + lr, ly + lr), fill="white", outline="#2c3e5e", width=12 * S)
lens = Image.new("RGBA", (W, W), (0, 0, 0, 0))
ld = ImageDraw.Draw(lens)
ld.ellipse(P(lx - lr + 8, ly - lr + 8, lx + lr - 8, ly + lr - 8), fill=(160, 210, 255, 70))
ld.arc(P(lx - lr + 20, ly - lr + 20, lx + lr - 20, ly + lr - 20), 200, 260, fill=(255, 255, 255, 200), width=7 * S)
im = Image.alpha_composite(im.convert("RGBA"), lens).convert("RGB")
d = ImageDraw.Draw(im)
title = ImageFont.truetype(GEORGIA, TITLE_PT * S)
d.text((256 * S, 438 * S), "LES DÉTECTIVES", font=title, fill="#f2c14e", anchor="mm")
d.text((256 * S, 470 * S), "DU GRAND LIVRE", font=title, fill="#f2c14e", anchor="mm")
d.text((256 * S, 496 * S), "LIRE LE PROFIT DANS LES TEXTES D'AUTREFOIS", font=ImageFont.truetype(HELV, TAG_PT * S - 2 * S), fill="#cdd6e6", anchor="mm")
mask = Image.new("L", (W, W), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, W, W], radius=70 * S, fill=255)
out = Image.new("RGB", (W, W), "white")
out.paste(im, mask=mask)
out.resize((512, 512), Image.LANCZOS).save(Path(__file__).resolve().parents[2] / "competition" / "logo.png")
