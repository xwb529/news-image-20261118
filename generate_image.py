"""Compose the specified newspaper front page with Pillow, entirely offline."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SCALE = 2
SIDE = 1024
MAX_BYTES = 1_048_576
PAPER = "#F7F3E9"
INK = "#152A34"
RED = "#A82D26"
TEAL = "#185D6D"
RULE = "#9AA5A1"
FONTS = Path("/usr/share/fonts/truetype")
FONT_FILES = {
    "masthead": "dejavu/DejaVuSerif-Bold.ttf",
    "bold": "liberation/LiberationSans-Bold.ttf",
    "regular": "liberation/LiberationSans-Regular.ttf",
    "italic": "liberation/LiberationSans-Italic.ttf",
}

STORIES = (
    (
        "chip",
        "NVIDIA HITS $115.8B REVENUE, BOARD BARS HUANG RETURN.",
        "Revenue up 103% year on year; Kress stays on as interim CEO.",
    ),
    (
        "health",
        "U.S. LOSES MEASLES ELIMINATION STATUS AFTER 26 YEARS.",
        "PAHO ends 26-year status; over 5,400 cases in 2026, most since 1991.",
    ),
    (
        "plane",
        "TRUMP JOINS QUAD SUMMIT IN MANILA AHEAD OF CHINA TRIP.",
        "Leaders unveil naval drills plus AI and cyber initiatives.",
    ),
    (
        "rocket",
        "U.S. HITS IRAN MISSILE SITE AFTER BAHRAIN BASE ATTACK.",
        "CENTCOM says all drones intercepted before strike on Qeshm Island.",
    ),
    (
        "house",
        "UK LAUNCHES 'BE READY' DRIVE URGING 3-DAY HOME STOCKPILES.",
        "Cabinet Office urges every home to store 3 days of food and water.",
    ),
)


def scaled_box(box: tuple[float, ...]) -> tuple[int, ...]:
    return tuple(round(value * SCALE) for value in box)


def main() -> None:
    page = Image.new("RGB", (SIDE * SCALE, SIDE * SCALE), PAPER)
    draw = ImageDraw.Draw(page)
    fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
    placements: list[tuple[str, tuple[int, int, int, int]]] = []

    def text(
        x: float,
        y: float,
        content: str,
        face: str,
        size: int,
        color: str = INK,
        *,
        right: bool = False,
    ) -> tuple[int, int, int, int]:
        key = (face, size)
        if key not in fonts:
            fonts[key] = ImageFont.truetype(str(FONTS / FONT_FILES[face]), size * SCALE)
        font = fonts[key]
        position = (round(x * SCALE), round(y * SCALE))
        if right:
            measured = draw.textbbox((0, position[1]), content, font=font)
            position = (position[0] - measured[2], position[1])
        bounds = draw.textbbox(position, content, font=font)
        assert 0 <= bounds[0] < bounds[2] <= SIDE * SCALE, (content, bounds)
        assert 0 <= bounds[1] < bounds[3] <= SIDE * SCALE, (content, bounds)
        assert bounds[0] >= 32 * SCALE and bounds[2] <= 992 * SCALE, (
            "Text exceeds the newspaper margins",
            content,
            bounds,
        )
        draw.text(position, content, font=font, fill=color)
        placements.append((content, bounds))
        return bounds

    def rule(y: float, width: int = 1, color: str = RULE) -> None:
        draw.line(scaled_box((32, y, 992, y)), fill=color, width=width * SCALE)

    def icon(kind: str, y: float) -> None:
        # Each symbol fits a 72 x 50 point box inside its 57-point row.
        ox, oy = 36, y + 4

        def polygon(points: list[tuple[float, float]], color: str = TEAL) -> None:
            draw.polygon(
                [(round((ox + x) * SCALE), round((oy + yy) * SCALE)) for x, yy in points],
                fill=color,
            )

        def rectangle(box: tuple[float, ...], color: str = TEAL) -> None:
            x1, y1, x2, y2 = box
            draw.rectangle(scaled_box((ox + x1, oy + y1, ox + x2, oy + y2)), fill=color)

        def ellipse(
            box: tuple[float, ...], color: str, *, outline: bool = False
        ) -> None:
            x1, y1, x2, y2 = box
            # A four-point ring remains visible in a 300-pixel-wide preview.
            kwargs = {"outline": color, "width": 4 * SCALE} if outline else {"fill": color}
            draw.ellipse(scaled_box((ox + x1, oy + y1, ox + x2, oy + y2)), **kwargs)

        if kind == "chip":
            rectangle((18, 8, 54, 44))
            for pin in (23, 32, 41, 50):
                draw.line(scaled_box((ox + pin, oy + 2, ox + pin, oy + 49)), fill=TEAL, width=2 * SCALE)
            for pin in (13, 22, 31, 40):
                draw.line(scaled_box((ox + 12, oy + pin, ox + 60, oy + pin)), fill=TEAL, width=2 * SCALE)
            rectangle((26, 16, 46, 36), PAPER)
            rectangle((30, 20, 42, 32))
        elif kind == "health":
            ellipse((12, 1, 60, 49), RED, outline=True)
            rectangle((31, 10, 41, 40), RED)
            rectangle((21, 20, 51, 30), RED)
        elif kind == "plane":
            polygon([
                (35, 1), (39, 7), (39, 19), (66, 33), (66, 38),
                (39, 31), (39, 42), (48, 47), (48, 50), (36, 47),
                (24, 50), (24, 47), (33, 42), (33, 31), (6, 38),
                (6, 33), (33, 19), (33, 7),
            ])
        elif kind == "rocket":
            polygon([(36, 1), (46, 14), (46, 36), (26, 36), (26, 14)])
            polygon([(26, 25), (18, 38), (18, 44), (29, 36)])
            polygon([(46, 25), (54, 38), (54, 44), (43, 36)])
            polygon([(30, 39), (36, 50), (42, 39)], RED)
            ellipse((32, 15, 40, 23), PAPER)
        elif kind == "house":
            polygon([(6, 24), (36, 1), (66, 24), (60, 29), (36, 11), (12, 29)])
            rectangle((16, 26, 56, 49))
            rectangle((31, 33, 41, 49), PAPER)
            rectangle((21, 31, 27, 38), PAPER)
            rectangle((45, 31, 51, 38), PAPER)
        else:
            raise ValueError(f"Unknown icon: {kind}")

    text(32, 12, "THE GLOBAL DAILY", "masthead", 60)
    rule(80, 4, INK)
    dateline = text(32, 89, "WEDNESDAY, NOVEMBER 18, 2026.", "bold", 28)
    edition = text(992, 89, "WORLD EDITION | VOL. CLIV NO. 322.", "regular", 16, right=True)
    assert dateline[2] + 16 * SCALE < edition[0], "Dateline and edition overlap"
    assert max(dateline[3], edition[3]) < 124 * SCALE
    rule(124)

    for index, (headline, color) in enumerate((
        ("BRIDGE WAR ESCALATES:", RED),
        ("KYIV BRIDGES HIT AFTER", INK),
        ("RECORD 1,441-DRONE STRIKE", INK),
    )):
        text(32, 134 + 60 * index, headline, "bold", 50, color)

    for index, line in enumerate((
        "Ukraine strikes Kerch Bridge for a second day; Russia retaliates",
        "on Kyiv river crossings, cutting power to 8 regions.",
    )):
        bounds = text(32, 322 + 27 * index, line, "regular", 22)
        assert bounds[3] < 384 * SCALE

    with Image.open(ASSETS / "hero.jpg") as source:
        hero = source.convert("RGB").resize((960 * SCALE, 288 * SCALE), Image.Resampling.LANCZOS)
    page.paste(hero, (32 * SCALE, 384 * SCALE))
    draw.rectangle(scaled_box((32, 384, 992, 672)), outline=INK, width=3 * SCALE)
    caption = text(
        32, 680,
        "Smoke rises near a Kyiv bridge over the Dnipro River after retaliatory missile strikes, Nov. 18, 2026.",
        "italic", 16,
    )
    assert caption[3] < 708 * SCALE

    for index, (kind, headline, summary) in enumerate(STORIES):
        y = 708 + index * 57
        if index:
            rule(y)
        icon(kind, y)
        heading_bounds = text(146, y + 1, headline, "bold", 23)
        summary_bounds = text(146, y + 31, summary, "regular", 17)
        assert heading_bounds[3] < summary_bounds[1], (headline, "Overlapping story text")
        assert summary_bounds[3] < (y + 57) * SCALE, (summary, "Story exceeds row")

    rule(1000)
    left_footer = text(32, 1006, "WIRE SOURCES: BBC / AP / REUTERS / AFP / AL JAZEERA", "bold", 13)
    right_footer = text(992, 1006, "ILLUSTRATED DAILY SUMMARY.", "bold", 13, right=True)
    assert left_footer[2] + 16 * SCALE < right_footer[0], "Footer columns overlap"
    assert len(placements) == 21, "An expected text element is missing"

    final = page.resize((SIDE, SIDE), Image.Resampling.LANCZOS)
    destination = ASSETS / "entry.png"
    final.save(destination, "PNG", optimize=True)
    if destination.stat().st_size > MAX_BYTES:
        final = final.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
        final.save(destination, "PNG", optimize=True)
    with Image.open(destination) as saved:
        assert saved.format == "PNG", saved.format
        assert saved.size == (1024, 1024), saved.size
        saved.verify()
    byte_size = destination.stat().st_size
    assert byte_size <= MAX_BYTES, byte_size
    print(f"Created {destination.name}: 1024x1024, {byte_size} bytes; {len(placements)} text bounds checked")


if __name__ == "__main__":
    main()
