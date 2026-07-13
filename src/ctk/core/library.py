from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

LIBRARY_COLUMNS = [
    "asset_id", "asset_type", "name", "path", "extension", "size_bytes",
    "sha256", "created_at", "tags", "related_ids", "status",
]

MEDIA_EXTENSIONS = {
    ".wav": "audio", ".wave": "audio", ".mp3": "audio", ".aiff": "audio",
    ".aif": "audio", ".flac": "audio", ".m4a": "audio",
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".webp": "image",
    ".gif": "image", ".svg": "image",
    ".mp4": "video", ".mov": "video", ".mkv": "video", ".webm": "video",
    ".pdf": "document", ".txt": "document", ".md": "document", ".csv": "data",
}


@dataclass
class ScanResult:
    scanned: int
    indexed: int
    catalog_path: Path


def init_library(root: Path) -> Path:
    root = root.expanduser().resolve()
    for relative in (
        "music/masters", "music/instrumentals", "music/vocals", "music/stems",
        "music/exports", "images", "videos", "artwork", "merch", "documents", "catalog",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)
    catalog = root / "catalog" / "library.csv"
    if not catalog.exists():
        with catalog.open("w", newline="", encoding="utf-8") as handle:
            csv.DictWriter(handle, fieldnames=LIBRARY_COLUMNS).writeheader()
    return catalog


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _asset_id(path: Path, sha256: str) -> str:
    prefix = MEDIA_EXTENSIONS.get(path.suffix.lower(), "asset")[:3].upper()
    return f"CTK-{prefix}-{sha256[:12].upper()}"


def scan_library(root: Path) -> ScanResult:
    root = root.expanduser().resolve()
    catalog = init_library(root)
    rows: list[dict[str, str | int]] = []
    scanned = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or catalog == path:
            continue
        if ".git" in path.parts or path.name.startswith("."):
            continue
        scanned += 1
        extension = path.suffix.lower()
        asset_type = MEDIA_EXTENSIONS.get(extension, "other")
        sha256 = _hash_file(path)
        rows.append({
            "asset_id": _asset_id(path, sha256),
            "asset_type": asset_type,
            "name": path.stem,
            "path": str(path.relative_to(root)),
            "extension": extension,
            "size_bytes": path.stat().st_size,
            "sha256": sha256,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": "",
            "related_ids": "",
            "status": "active",
        })
    with catalog.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=LIBRARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return ScanResult(scanned=scanned, indexed=len(rows), catalog_path=catalog)


def validate_library(root: Path) -> list[str]:
    root = root.expanduser().resolve()
    catalog = root / "catalog" / "library.csv"
    errors: list[str] = []
    if not root.exists():
        return [f"library path does not exist: {root}"]
    if not catalog.exists():
        return [f"library catalog missing: {catalog}"]
    with catalog.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != LIBRARY_COLUMNS:
            errors.append("library.csv columns do not match the CTK Library schema")
        seen: set[str] = set()
        for number, row in enumerate(reader, start=2):
            asset_id = row.get("asset_id", "")
            if not asset_id:
                errors.append(f"row {number}: asset_id is required")
            elif asset_id in seen:
                errors.append(f"row {number}: duplicate asset_id {asset_id}")
            seen.add(asset_id)
            relative_path = row.get("path", "")
            if relative_path and not (root / relative_path).exists():
                errors.append(f"row {number}: missing asset {relative_path}")
    return errors
