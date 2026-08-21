#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
METADATA = ROOT / "_data" / "acm-confirmed-metadata.csv"
OBJECTS = ROOT / "objects"
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}


def build_object_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for path in OBJECTS.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_EXTS:
            continue
        lookup[path.stem.lower()] = f"/objects/{path.name}"
    return lookup


def sync_metadata() -> int:
    with METADATA.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise RuntimeError("Metadata CSV has no header row.")
        rows = list(reader)

    object_lookup = build_object_lookup()
    updates = 0

    for row in rows:
        objectid = (row.get("objectid") or "").strip()
        if not objectid:
            continue
        actual_path = object_lookup.get(objectid.lower())
        if not actual_path:
            continue
        for field in ("object_location", "image_small", "image_thumb"):
            if row.get(field) != actual_path:
                row[field] = actual_path
                updates += 1

    with METADATA.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return updates


if __name__ == "__main__":
    changed = sync_metadata()
    print(f"Synchronized object paths in {METADATA.name}: {changed} field updates")
