"""Creative catalog tools for CallMeTK OS."""
from __future__ import annotations

import csv
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .naming import NamingRecord, slugify, validate_ctk_id, validate_slug

CATALOG_COLUMNS = [
    "ctk_id",
    "name",
    "slug",
    "type",
    "status",
    "source_path",
    "related_to",
    "tags",
    "notes",
]

MUSIC_COLUMNS = [
    "track_id",
    "ctk_id",
    "title",
    "artist",
    "file",
    "bpm",
    "key",
    "mood",
    "energy",
    "use_case",
    "loop",
    "start_time",
    "end_time",
    "tags",
    "notes",
]

GAME_LEVEL_COLUMNS = ["level_id", "name", "type", "difficulty", "bgm_track_id", "notes"]
GAME_ITEMS_COLUMNS = ["item_id", "name", "type", "value", "tags", "notes"]
GAME_DIALOGUE_COLUMNS = ["dialogue_id", "speaker", "text", "scene", "tags"]
GAME_ACHIEVEMENTS_COLUMNS = ["achievement_id", "name", "description", "reward_ctk_id", "points"]

AUDIO_EXTENSIONS = {".mp3", ".wav", ".aiff", ".aif", ".flac", ".m4a", ".ogg"}


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows or []:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def validate_required_csv(path: Path, required_columns: list[str]) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"CSV not found: {path}"]
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        for column in required_columns:
            if column not in columns:
                errors.append(f"Missing required column: {column}")
        for index, row in enumerate(reader, start=2):
            if "ctk_id" in columns and row.get("ctk_id") and not validate_ctk_id(row["ctk_id"]):
                errors.append(f"Row {index}: invalid ctk_id '{row['ctk_id']}'")
            if "slug" in columns and row.get("slug") and not validate_slug(row["slug"]):
                errors.append(f"Row {index}: invalid slug '{row['slug']}'")
    return errors


def init_catalog(path: Path) -> Path:
    write_csv(path, CATALOG_COLUMNS)
    return path


def add_catalog_item(path: Path, item_type: str, name: str, source_path: str = "", tags: str = "", notes: str = "") -> dict[str, str]:
    if not path.exists():
        init_catalog(path)
    record = NamingRecord.create(item_type, name)
    row = {
        "ctk_id": record.ctk_id,
        "name": record.name,
        "slug": record.slug,
        "type": record.type,
        "status": "draft",
        "source_path": source_path,
        "related_to": "",
        "tags": tags,
        "notes": notes,
    }
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CATALOG_COLUMNS)
        writer.writerow(row)
    return row


def init_music_csv(path: Path) -> Path:
    write_csv(path, MUSIC_COLUMNS)
    return path


def import_music_folder(folder: Path, output_csv: Path, artist: str = "CallMe TK") -> int:
    tracks = sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS)
    rows: list[dict[str, str]] = []
    for index, track in enumerate(tracks, start=1):
        title = track.stem.replace("_", " ").replace("-", " ").title()
        record = NamingRecord.create("song", title)
        rows.append({
            "track_id": f"MUS{index:03d}",
            "ctk_id": record.ctk_id,
            "title": title,
            "artist": artist,
            "file": str(track),
            "bpm": "",
            "key": "",
            "mood": "",
            "energy": "",
            "use_case": "catalog",
            "loop": "false",
            "start_time": "0",
            "end_time": "",
            "tags": "",
            "notes": "Imported by CTK OS",
        })
    write_csv(output_csv, MUSIC_COLUMNS, rows)
    return len(rows)


def init_game_data(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    write_csv(data_dir / "music.csv", MUSIC_COLUMNS, [])
    write_csv(data_dir / "levels.csv", GAME_LEVEL_COLUMNS, [
        {"level_id": "LV001", "name": "Opening Level", "type": "level", "difficulty": "easy", "bgm_track_id": "", "notes": "Starter level"}
    ])
    write_csv(data_dir / "items.csv", GAME_ITEMS_COLUMNS, [])
    write_csv(data_dir / "dialogue.csv", GAME_DIALOGUE_COLUMNS, [])
    write_csv(data_dir / "achievements.csv", GAME_ACHIEVEMENTS_COLUMNS, [])
    write_csv(data_dir / "catalog.csv", CATALOG_COLUMNS, [])
