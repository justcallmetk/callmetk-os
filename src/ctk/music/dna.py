from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def _float(row: dict[str, str], key: str) -> float | None:
    try:
        raw = row.get(key, "")
        return float(raw) if raw not in ("", None) else None
    except ValueError:
        return None


def build_creative_dna(path: Path) -> dict[str, object]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("analysis_status", "complete") == "complete"]
    def average(key: str) -> float:
        values = [value for row in rows if (value := _float(row, key)) is not None]
        return round(sum(values) / len(values), 3) if values else 0.0
    keys = Counter(row.get("musical_key", "unknown") for row in rows if row.get("musical_key", "unknown") != "unknown")
    return {
        "tracks": len(rows),
        "total_runtime_seconds": round(sum(_float(row, "duration_seconds") or 0.0 for row in rows), 3),
        "average_duration_seconds": average("duration_seconds"),
        "average_tempo_bpm": average("tempo_bpm"),
        "average_energy": average("energy"),
        "average_brightness": average("brightness"),
        "most_common_keys": [key for key, _ in keys.most_common(3)],
        "analysis_scope": "local deterministic features",
    }
