#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent
OBJECTS = ROOT / "objects"
BROWSE = OBJECTS / "browse"
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
MAX_SIZE = (1200, 1200)
JPEG_QUALITY = 82


def iter_source_images() -> list[Path]:
    return [
        path
        for path in sorted(OBJECTS.iterdir())
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTS
    ]


def make_rgb(image: Image.Image) -> Image.Image:
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, "white")
        alpha = image.getchannel("A")
        background.paste(image.convert("RGBA"), mask=alpha)
        return background
    if image.mode == "P":
        return image.convert("RGB")
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def generate_derivative(source: Path) -> None:
    destination = BROWSE / f"{source.stem}.jpg"
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image)
        image = make_rgb(image)
        image.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(
            destination,
            format="JPEG",
            optimize=True,
            progressive=True,
            quality=JPEG_QUALITY,
        )


def main() -> None:
    BROWSE.mkdir(parents=True, exist_ok=True)
    sources = iter_source_images()
    valid_stems = {path.stem for path in sources}
    generated = 0

    for stale in BROWSE.glob("*.jpg"):
        if stale.stem not in valid_stems:
            stale.unlink()

    for source in sources:
        derivative = BROWSE / f"{source.stem}.jpg"
        if derivative.exists():
            src_stat = source.stat()
            dst_stat = derivative.stat()
            if dst_stat.st_mtime >= src_stat.st_mtime and dst_stat.st_size > 0:
                continue
        generate_derivative(source)
        generated += 1

    print(f"Generated browse derivatives: {generated} updated, {len(sources)} total")


if __name__ == "__main__":
    main()
