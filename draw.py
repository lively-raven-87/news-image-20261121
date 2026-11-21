#!/usr/bin/env python3
"""Render 'The World — 21 November 2026' as a 1024x1024 newspaper page.

Draws the verified 21 Nov 2026 brief (Mexico cartel-boss capture leads;
market sell-off, Kryvyi Rih/Poland missiles, Iran/Hormuz, COP31 follow)
with Pillow and writes entry.png beside this file.
"""

import os

from PIL import Image, ImageDraw, ImageFont

PAGE = (1024, 1024)
EDGE = 36
SPAN = PAGE[0] - 2 * EDGE

PAPER = (248, 244, 233)
INK = (20, 20, 20)
BODY_GREY = (60, 58, 50)
MUTED = (90, 86, 76)
RED = (176, 30, 30)
FAINT_RULE = (150, 145, 130)
CARD = (255, 253, 245)
BAND = (18, 18, 18)
BAND_TEXT = (245, 242, 232)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

LEAD_HEAD = "FBI Most-Wanted Cartel Boss Captured in Mexico"
LEAD_DECK = ("Mexican forces seized Fausto Isidro Meza Flores — "
             "\u201cEl Chapo Isidro\u201d — in Guasave, Sinaloa, after a "
             "shootout that shook the cartel heartland.")
LEAD_BODY = ("Troops moved in on the Sinaloa stronghold and took Meza "
             "Flores alive. He sits on the FBI's list of its ten "
             "most-wanted fugitives. Eleven people were killed in the "
             "violence that followed the arrest.")

FACTS = [
    ("WHO", "Fausto Isidro Meza Flores (\u201cEl Chapo Isidro\u201d)"),
    ("WHERE", "Guasave, Sinaloa, Mexico"),
    ("DEAD", "11 killed in aftermath violence"),
    ("STATUS", "In custody"),
]

STORIES = [
    {"kick": "MARKETS PLUNGE",
     "head": "Stocks tumble as AI rally cracks",
     "body": "S&P 500 fell 3.7% on Friday; Nikkei slid 5.06% and Hang Seng "
             "3.79%. Wall Street's main indexes entered correction "
             "territory, down 10% or more from their peaks. Nvidia halted "
             "exports of its H200 AI chips to China."},
    {"kick": "WAR IN UKRAINE",
     "head": "Missiles hit Kryvyi Rih and Poland",
     "body": "A Russian ballistic missile struck Kryvyi Rih, President "
             "Zelensky's home city: 2 killed, 60 wounded. Another Russian "
             "missile landed in Poland during NATO drills; NATO called it "
             "a violation."},
    {"kick": "IRAN & THE GULF",
     "head": "Trump weighs a new strike on Iran",
     "body": "Trump is considering fresh strikes as Israel urges swift "
             "action, the NYT reports. Iran unveiled new missile launchers "
             "in an underground base and claims it downed a U.S. drone "
             "over Hormuz. Tanker attacks near the strait hit a monthly "
             "record."},
    {"kick": "CLIMATE — COP31",
     "head": "Climate summit blows past deadline",
     "body": "COP31 in Antalya, Turkey, missed its Friday deadline. A "
             "revised draft weakened or removed language on fossil fuels, "
             "drawing fire from delegates pushing for a stronger deal "
             "before talks close."},
]

TICKER = ("PERU QUAKE 6.7  •  DENMARK TO EXPEL RUSSIAN ENVOY  •  "
          "ANTHROPIC IPO: $81.3BN  •  ASEAN SUMMIT OPENS IN MANILA")
CREDIT = "Sources: AP  •  NYT  •  KIRO 7  •  One Turn News  •  Standard Topic"


class Page:
    """A 1024x1024 newspaper sheet with text helpers."""

    def __init__(self):
        self.img = Image.new("RGB", PAGE, PAPER)
        self.d = ImageDraw.Draw(self.img)

    def load(self, path, size):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            return ImageFont.load_default()

    def flow(self, text, fnt, width):
        """Greedy wrap on pixel width; returns the lines."""
        out = []
        for chunk in text.split("\n"):
            words = chunk.split()
            if not words:
                out.append("")
                continue
            line = words[0]
            for w in words[1:]:
                cand = line + " " + w
                if self.d.textlength(cand, font=fnt) <= width:
                    line = cand
                else:
                    out.append(line)
                    line = w
            out.append(line)
        return out

    def para(self, lines, x, y, fnt, fill=INK, gap=None, centre=False):
        """Draw lines; returns the y just below the block."""
        step = gap if gap is not None else int(fnt.size * 1.28)
        for ln in lines:
            lx = x
            if centre:
                lx = x + (SPAN - self.d.textlength(ln, font=fnt)) / 2
            self.d.text((lx, y), ln, font=fnt, fill=fill)
            y += step
        return y

    def mid(self, text, y, fnt, fill=INK):
        self.d.text(((PAGE[0] - self.d.textlength(text, font=fnt)) / 2, y),
                    text, font=fnt, fill=fill)
        return y + int(fnt.size * 1.3)

    def hline(self, y, thick=2, fill=INK, x0=None, x1=None):
        self.d.line([(x0 or EDGE, y), (x1 or PAGE[0] - EDGE, y)],
                    fill=fill, width=thick)
        return y + thick


def glance_box(page, x, y, width):
    """The 'AT A GLANCE' fact box; returns its bottom y."""
    lab_f = page.load(F_SANS_B, 15)
    val_f = page.load(F_SERIF, 16)
    val_w = width - 16 - 74 - 16
    rows = [(lab, page.flow(val, val_f, val_w)) for lab, val in FACTS]
    n_val = sum(len(v) for _, v in rows)
    top = y - 4
    tall = 12 + 26 + 10 + n_val * 22 + 8 + 18 + 12
    page.d.rectangle([x, top, x + width, top + tall], fill=CARD,
                     outline=INK, width=2)
    bx, by = x + 16, top + 12
    page.d.text((bx, by), "AT A GLANCE", font=page.load(F_SANS_B, 16),
                fill=RED)
    by += 26
    page.d.line([(bx, by), (x + width - 16, by)], fill=FAINT_RULE, width=1)
    by += 10
    for lab, vlines in rows:
        page.d.text((bx, by), lab, font=lab_f, fill=RED)
        vy = by
        for vline in vlines:
            page.d.text((bx + 74, vy - 1), vline, font=val_f, fill=INK)
            vy += 22
        by = vy
    by += 6
    page.d.text((bx, by), "Sources: AP, KIRO 7",
                font=page.load(F_SERIF_I, 14), fill=MUTED)
    return top + tall


def card(page, story, x, y, width):
    """One secondary story: kicker, headline, body."""
    page.d.text((x, y), story["kick"], font=page.load(F_SANS_B, 15),
                fill=RED)
    hy = y + 22
    head_f = page.load(F_SERIF_B, 23)
    hy = page.para(page.flow(story["head"], head_f, width), x, hy,
                   head_f, gap=26)
    body_f = page.load(F_SERIF, 17)
    page.para(page.flow(story["body"], body_f, width), x, hy + 2,
              body_f, gap=21)


def build():
    p = Page()
    d = p.d

    p.mid("SATURDAY EDITION  •  VOL. 2026 — NO. 325", 18,
          p.load(F_SANS, 15), fill=MUTED)
    p.mid("THE WORLD", 40, p.load(F_SERIF_B, 88))
    p.hline(156)
    p.hline(160, thick=1)
    p.mid("21 NOVEMBER 2026", 168, p.load(F_SANS_B, 21))
    p.hline(200)

    y = 214
    d.text((EDGE, y), "LEAD STORY  —  MEXICO",
           font=p.load(F_SANS_B, 19), fill=RED)
    y += 28
    head_f = p.load(F_SERIF_B, 42)
    y = p.para(p.flow(LEAD_HEAD, head_f, SPAN), EDGE, y, head_f, gap=48)
    y += 4
    deck_f = p.load(F_SERIF_I, 21)
    y = p.para(p.flow(LEAD_DECK, deck_f, SPAN), EDGE, y, deck_f,
               fill=BODY_GREY, gap=28)
    y += 8

    body_w = 520
    box_x = EDGE + body_w + 26
    box_w = PAGE[0] - EDGE - box_x
    body_f = p.load(F_SERIF, 20)
    body_end = p.para(p.flow(LEAD_BODY, body_f, body_w), EDGE, y,
                      body_f, gap=26)
    box_end = glance_box(p, box_x, y, box_w)

    y = max(body_end, box_end) + 14
    p.hline(y)
    y += 12

    col = (SPAN - 28) // 2
    row_h = 148
    for i, story in enumerate(STORIES):
        cx = EDGE + (i % 2) * (col + 28)
        cy = y + (i // 2) * (row_h + 12)
        card(p, story, cx, cy, col)
        if i % 2 == 0:
            d.line([(cx + col + 14, cy), (cx + col + 14, cy + row_h)],
                   fill=FAINT_RULE, width=1)

    y = y + 2 * row_h + 10 + 6
    p.hline(y)
    y += 10

    band_h = 36
    d.rectangle([EDGE, y, PAGE[0] - EDGE, y + band_h], fill=BAND)
    tick_f = p.load(F_SANS_B, 15)
    p.mid(TICKER, y + 10, tick_f, fill=BAND_TEXT)
    p.mid(CREDIT, y + band_h + 10, p.load(F_SANS, 13), fill=MUTED)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    p.img.save(out, format="PNG", optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
