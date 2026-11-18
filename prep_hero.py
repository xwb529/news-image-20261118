"""Prepare the supplied photograph for the front-page hero band."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE = Path(
    "/home/hatch/workspace/makefun/news-image-art/"
    "media-generation-news-image-20261118-hero-bridg-0-"
    "ed788164-7d71-4330-9b9c-3ea70fdb5973.webp"
)


def main() -> None:
    destination = ROOT / "assets" / "hero.jpg"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as source:
        hero = source.crop((0, 205, 2352, 911)).convert("RGB")
        hero = hero.resize((1920, 576), Image.Resampling.LANCZOS)
        hero.save(destination, "JPEG", quality=88)
    print(f"Prepared {destination.name}: 1920x576, {destination.stat().st_size} bytes")


if __name__ == "__main__":
    main()
