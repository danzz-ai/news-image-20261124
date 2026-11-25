#!/usr/bin/env python3
"""Render 'The World Today - 24 November 2026' as a 1024x1024 broadsheet front page.

Draws the whole page from the news spec with PIL only. Deterministic: no
timestamps, no randomness, fixed fonts and geometry, so two runs produce
byte-identical output.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

INK = (17, 17, 17)
PAPER = (255, 255, 255)
ACCENT = (139, 26, 26)
GREY = (120, 120, 120)
LIGHT_GREY = (210, 210, 210)
GOLD = (255, 210, 120)

FONT_DIR = "/usr/share/fonts/truetype/liberation"
SERIF = os.path.join(FONT_DIR, "LiberationSerif-Regular.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "LiberationSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def line_advance(fnt):
    """Full line height (ascent + descent) so stacked lines never overlap."""
    asc, desc = fnt.getmetrics()
    return asc + desc


def text_w(draw, text, fnt):
    return draw.textbbox((0, 0), text, font=fnt)[2]


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, cx, y, text, fnt, fill=INK):
    w = text_w(draw, text, fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def draw_wrapped_centered(draw, cx, y, lines, fnt, leading, fill=INK):
    for line in lines:
        draw_centered(draw, cx, y, line, fnt, fill)
        y += leading
    return y


def draw_wrapped_left(draw, x, y, lines, fnt, leading, fill=INK):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_lines(draw, text, fnt, max_w, max_lines, min_size, path):
    """Shrink the font until the headline fits in max_lines, return (font, lines)."""
    size = fnt.size
    while size > min_size:
        f = font(path, size)
        lines = wrap(draw, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 2
    f = font(path, min_size)
    return f, wrap(draw, text, f, max_w)


def draw_tanker_scene(draw, x0, y0, x1, y1):
    """Schematic ink drawing: an oil tanker at sea with a naval mine ahead."""
    sea_top = y0 + int((y1 - y0) * 0.55)
    draw.rectangle([x0, sea_top, x1, y1], fill=(235, 238, 240))
    for i, wy in enumerate((sea_top + 12, sea_top + 26)):
        amp = 5 if i % 2 == 0 else 4
        pts = []
        xx = x0
        while xx <= x1:
            pts.append((xx, wy + amp * ((xx // 26) % 2 * 2 - 1)))
            xx += 13
        draw.line(pts, fill=INK, width=2)
    # hull: long low slab with a tapered bow
    hull_y = sea_top - 26
    hull = [
        (x0 + 30, hull_y),
        (x1 - 170, hull_y),
        (x1 - 70, hull_y + 22),
        (x1 - 70, sea_top + 4),
        (x0 + 30, sea_top + 4),
    ]
    draw.polygon(hull, fill=INK)
    # cargo hatches sitting on the deck, dark with pale seams
    for hx in range(x0 + 150, x1 - 230, 72):
        draw.rectangle([hx, hull_y - 14, hx + 50, hull_y], fill=INK)
        draw.rectangle([hx, hull_y - 14, hx + 50, hull_y], outline=(200, 200, 200), width=1)
    # stern superstructure with lit windows
    draw.rectangle([x0 + 34, hull_y - 46, x0 + 116, hull_y], fill=INK)
    for wy in range(hull_y - 40, hull_y - 6, 12):
        draw.line([(x0 + 42, wy), (x0 + 108, wy)], fill=PAPER, width=2)
    # funnel with accent band
    draw.rectangle([x0 + 124, hull_y - 58, x0 + 150, hull_y], fill=INK)
    draw.rectangle([x0 + 124, hull_y - 58, x0 + 150, hull_y - 44], fill=ACCENT)
    # bow mast
    draw.line([(x1 - 110, hull_y - 34), (x1 - 110, hull_y)], fill=INK, width=3)
    draw.line([(x1 - 110, hull_y - 34), (x1 - 82, hull_y - 24)], fill=INK, width=2)
    # naval mine ahead of the bow, half submerged, with a red blast starburst
    mx, my, mr = x1 - 108, sea_top - 2, 12
    for k in range(12):
        ang = math.pi * k / 6
        outer = mr + 16 if k % 2 == 0 else mr + 9
        ex = mx + int(outer * math.cos(ang))
        ey = my + int(outer * math.sin(ang))
        draw.line([(mx, my), (ex, ey)], fill=ACCENT, width=2)
    for k in range(8):
        ang = math.pi * k / 4
        ex = mx + int((mr + 9) * math.cos(ang))
        ey = my + int((mr + 9) * math.sin(ang))
        draw.line([(mx, my), (ex, ey)], fill=INK, width=3)
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=INK)
    # a second, smaller mine drifting further out to sea
    mx2, my2, mr2 = x0 + 210, sea_top + 22, 9
    for k in range(8):
        ang = math.pi * k / 4
        ex = mx2 + int((mr2 + 7) * math.cos(ang))
        ey = my2 + int((mr2 + 7) * math.sin(ang))
        draw.line([(mx2, my2), (ex, ey)], fill=INK, width=2)
    draw.ellipse([mx2 - mr2, my2 - mr2, mx2 + mr2, my2 + mr2], fill=INK)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 20

    # ---- Masthead ----
    mast = font(SERIF_BOLD, 86)
    draw_centered(d, W // 2, y, "THE WORLD TODAY", mast)
    y += line_advance(mast) - 8

    # ---- Date line with flanking rules ----
    date_f = font(SANS_BOLD, 19)
    date_txt = "T U E S D A Y ,  2 4  N O V E M B E R  2 0 2 6"
    dw = text_w(d, date_txt, date_f)
    asc, _ = date_f.getmetrics()
    rule_y = y + asc // 2
    d.line([(MARGIN, rule_y), (W // 2 - dw // 2 - 18, rule_y)], fill=INK, width=2)
    d.line([(W // 2 + dw // 2 + 18, rule_y), (W - MARGIN, rule_y)], fill=INK, width=2)
    draw_centered(d, W // 2, y, date_txt, date_f)
    y += line_advance(date_f) + 8

    # ---- Double rule under the masthead ----
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=3)
    y += 5
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=1)
    y += 14

    # ---- Hero kicker ----
    kick_f = font(SANS_BOLD, 19)
    draw_centered(d, W // 2, y, "S T R A I T   O F   H O R M U Z", kick_f, ACCENT)
    y += line_advance(kick_f) + 6

    # ---- Hero headline, fitted to two lines ----
    hero_f, hero_lines = fit_lines(
        d, "TANKERS HIT BY MINES IN HORMUZ",
        font(SERIF_BOLD, 62), CONTENT_W, 2, 40, SERIF_BOLD,
    )
    y = draw_wrapped_centered(d, W // 2, y, hero_lines, hero_f, int(hero_f.size * 1.02))
    y += 8

    # ---- Hero standfirst ----
    stand = (
        "Iran says three oil tankers struck mines in the Strait of Hormuz late Monday "
        "despite a US escort; the US Treasury sanctioned more than two dozen Iranian "
        "exchange houses; Tehran refuses talks until seven conditions are met."
    )
    stand_f = font(SERIF, 22)
    stand_lines = wrap(d, stand, stand_f, CONTENT_W - 60)
    y = draw_wrapped_centered(d, W // 2, y, stand_lines, stand_f, 29, fill=(40, 40, 40))
    y += 10

    # ---- Hero illustration ----
    art_top = y
    art_h = 106
    draw_tanker_scene(d, MARGIN, art_top, W - MARGIN, art_top + art_h)
    y = art_top + art_h + 10
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=INK, width=2)
    y += 12

    # ---- Six panels, 3 columns x 2 rows ----
    panels = [
        ("SPACE", "CHINA LAUNCHES SHENZHOU-24",
         "Two Chinese astronauts fly with Pakistani astronaut Zeeshan Ali, the first "
         "foreign astronaut aboard China's Tiangong space station."),
        ("JUSTICE", "14 NATIONS BACK ICJ ROHINGYA RULING",
         "The UK, Spain, Canada, Australia and ten others affirm the ICJ genocide "
         "ruling against Myanmar; the UK adds sanctions on senior military figures."),
        ("DIPLOMACY", "NORTH KOREA EXPELS SWISS ENVOY",
         "Pyongyang demands closure of Switzerland's new diplomatic office and "
         "orders its senior diplomat to leave."),
        ("PACIFIC", "SOLOMONS PICK AUSTRALIA",
         "Solomon Islands names Australia its primary security partner in a new "
         "treaty that excludes China."),
        ("TRADE", "US READY TO HIT CHINA, EU WITH TARIFFS",
         "Washington is ready to impose tariffs on China, the EU and others over "
         "subsidized production, AP sources say."),
        ("MARKETS", "MARKETS RALLY",
         "Nasdaq +6.51%, S&P 500 +4.73% at the 24 Nov close; Nikkei +3.91%; "
         "Brent crude $86.7, -2.99%; gold $3,620.4, -0.85%."),
    ]
    gutter = 22
    col_w = (CONTENT_W - 2 * gutter) // 3
    row_h = 168
    kick_s = font(SANS_BOLD, 15)
    head_f = font(SERIF_BOLD, 23)
    body_f = font(SERIF, 17)
    for idx, (label, headline, body) in enumerate(panels):
        row, col = divmod(idx, 3)
        x = MARGIN + col * (col_w + gutter)
        py = y + row * row_h
        if col > 0:
            d.line([(x - gutter // 2, py + 4), (x - gutter // 2, py + row_h - 18)],
                   fill=LIGHT_GREY, width=1)
        d.text((x, py), label, font=kick_s, fill=ACCENT)
        h_lines = wrap(d, headline, head_f, col_w)
        hy = draw_wrapped_left(d, x, py + 21, h_lines[:2], head_f, 26)
        b_lines = wrap(d, body, body_f, col_w)
        draw_wrapped_left(d, x, hy + 4, b_lines[:4], body_f, 21, fill=(40, 40, 40))
    y += 2 * row_h + 8

    # ---- Ticker strip ----
    tick_h = 78
    tick_y = H - 22 - tick_h
    d.rectangle([0, tick_y, W, tick_y + tick_h], fill=INK)
    tick_f = font(SANS, 15)
    tick_b = font(SANS_BOLD, 15)
    ticker = (
        "5.6-magnitude earthquake strikes Nepal near the Chinese border  |  "
        "Malaysia to return 6,500+ Rohingya refugees to Myanmar  |  "
        "FIFA names the US, Mexico, Costa Rica and Jamaica co-hosts of the 2031 "
        "Women's World Cup  |  Israeli drone strike near Khan Younis in Gaza kills three"
    )
    label_w = text_w(d, "ALSO TODAY   ", tick_b)
    t_lines = wrap(d, ticker, tick_f, CONTENT_W - label_w)
    ty = tick_y + 9
    d.text((MARGIN, ty), "ALSO TODAY", font=tick_b, fill=GOLD)
    first = t_lines[0] if t_lines else ""
    d.text((MARGIN + label_w, ty), first, font=tick_f, fill=PAPER)
    ty += 22
    for line in t_lines[1:3]:
        d.text((MARGIN, ty), line, font=tick_f, fill=PAPER)
        ty += 22

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out_path, "JPEG", quality=90, optimize=True)
    print("wrote", out_path, os.path.getsize(out_path), "bytes")


if __name__ == "__main__":
    main()
