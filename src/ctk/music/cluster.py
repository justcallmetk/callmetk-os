from __future__ import annotations

import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path

FEATURE_COLUMNS = ("tempo_bpm", "energy", "brightness", "duration_seconds")


@dataclass
class ClusterResult:
    assignments: list[dict[str, str | int | float]]
    clusters: int
    inertia: float


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _number(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "") or 0.0)
    except ValueError:
        return 0.0


def _standardize(matrix: list[list[float]]) -> list[list[float]]:
    if not matrix:
        return []
    columns = list(zip(*matrix))
    means = [sum(column) / len(column) for column in columns]
    stds = []
    for column, mean in zip(columns, means):
        variance = sum((value - mean) ** 2 for value in column) / max(1, len(column))
        stds.append(math.sqrt(variance) or 1.0)
    return [[(value - means[index]) / stds[index] for index, value in enumerate(row)] for row in matrix]


def _distance(left: list[float], right: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(left, right))


def cluster_tracks(input_csv: Path, output_csv: Path, clusters: int = 3, seed: int = 7) -> ClusterResult:
    rows = [row for row in _read_rows(input_csv) if row.get("analysis_status", "complete") == "complete"]
    if not rows:
        raise ValueError("no completed audio analyses available")
    clusters = max(1, min(clusters, len(rows)))
    vectors = _standardize([[_number(row, key) for key in FEATURE_COLUMNS] for row in rows])
    rng = random.Random(seed)
    centers = [vectors[index][:] for index in rng.sample(range(len(vectors)), clusters)]
    assignments = [0] * len(vectors)
    for _ in range(100):
        updated = [min(range(clusters), key=lambda index: _distance(vector, centers[index])) for vector in vectors]
        if updated == assignments and _ > 0:
            break
        assignments = updated
        new_centers: list[list[float]] = []
        for cluster_index in range(clusters):
            members = [vector for vector, assignment in zip(vectors, assignments) if assignment == cluster_index]
            if not members:
                new_centers.append(vectors[rng.randrange(len(vectors))][:])
            else:
                new_centers.append([sum(column) / len(column) for column in zip(*members)])
        centers = new_centers
    inertia = sum(_distance(vector, centers[assignment]) for vector, assignment in zip(vectors, assignments))
    output_rows: list[dict[str, str | int | float]] = []
    for row, assignment, vector in zip(rows, assignments, vectors):
        distance = math.sqrt(_distance(vector, centers[assignment]))
        cohesion = 1.0 / (1.0 + distance)
        output_rows.append({
            "track_id": row.get("track_id", ""),
            "title": row.get("title", ""),
            "cluster_id": assignment + 1,
            "cluster_label": f"Cluster {assignment + 1}",
            "cohesion": round(cohesion, 6),
            "tempo_bpm": _number(row, "tempo_bpm"),
            "energy": _number(row, "energy"),
            "brightness": _number(row, "brightness"),
            "duration_seconds": _number(row, "duration_seconds"),
        })
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0].keys())
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    return ClusterResult(assignments=output_rows, clusters=clusters, inertia=inertia)
