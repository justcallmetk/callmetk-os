from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from ctk.core.toast import ToastDecision


def build_ep_recommendation(cluster_csv: Path, tracks: int = 4, cluster_id: int | None = None) -> ToastDecision:
    with cluster_csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("cluster CSV contains no tracks")
    groups: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[int(row["cluster_id"])].append(row)
    selected_cluster = cluster_id if cluster_id in groups else max(groups, key=lambda key: (len(groups[key]), sum(float(row.get("cohesion", 0)) for row in groups[key])))
    candidates = sorted(groups[selected_cluster], key=lambda row: float(row.get("cohesion", 0)), reverse=True)
    chosen = candidates[: max(1, min(tracks, len(candidates)))]
    titles = [row.get("title", "Untitled") for row in chosen]
    runtime = sum(float(row.get("duration_seconds", 0) or 0) for row in chosen)
    avg_cohesion = sum(float(row.get("cohesion", 0) or 0) for row in chosen) / len(chosen)
    confidence = min(0.99, 0.55 + avg_cohesion * 0.4 + min(len(chosen), 5) * 0.01)
    alternatives = [row.get("title", "Untitled") for row in candidates[len(chosen):len(chosen) + 3]]
    primary_sequence = " | ".join(titles)
    option_sequences = [primary_sequence]
    if alternatives:
        option_sequences.append(" | ".join((titles[:-1] + [alternatives[0]]) if len(titles) > 1 else [alternatives[0]]))
    return ToastDecision(
        target=f"Build a cohesive {len(chosen)}-track mini EP",
        options=option_sequences,
        selection=primary_sequence,
        confidence=round(confidence, 4),
        reasoning=[
            f"Tracks share Cluster {selected_cluster} audio characteristics.",
            f"Average cluster cohesion is {avg_cohesion:.2%}.",
            f"Estimated runtime is {runtime / 60:.1f} minutes.",
            "This is a recommendation; sequencing and creative-domain review remain human-approved.",
        ],
        evidence=[
            {"metric": "cluster_id", "value": selected_cluster},
            {"metric": "track_count", "value": len(chosen)},
            {"metric": "runtime_seconds", "value": round(runtime, 2)},
            {"metric": "average_cohesion", "value": round(avg_cohesion, 4)},
        ],
        alternatives=alternatives,
        estimated_cost_usd=0.0,
        requires_approval=True,
    )
