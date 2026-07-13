from __future__ import annotations

import csv
import hashlib
import math
import struct
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

AUDIO_ANALYSIS_COLUMNS = [
    "track_id", "title", "path", "format", "duration_seconds", "sample_rate",
    "channels", "sample_width_bits", "peak", "rms", "energy", "brightness",
    "tempo_bpm", "musical_key", "analysis_status", "analysis_notes",
]

SUPPORTED_AUDIO = {".wav", ".wave"}


@dataclass
class AudioAnalysis:
    track_id: str
    title: str
    path: str
    format: str
    duration_seconds: float
    sample_rate: int
    channels: int
    sample_width_bits: int
    peak: float
    rms: float
    energy: float
    brightness: float
    tempo_bpm: float | None = None
    musical_key: str = "unknown"
    analysis_status: str = "complete"
    analysis_notes: str = ""

    def to_row(self) -> dict[str, str | int | float]:
        row = asdict(self)
        row["tempo_bpm"] = "" if self.tempo_bpm is None else round(self.tempo_bpm, 3)
        for key in ("duration_seconds", "peak", "rms", "energy", "brightness"):
            row[key] = round(float(row[key]), 6)
        return row


def _track_id(path: Path) -> str:
    digest = hashlib.sha256(str(path.resolve()).encode("utf-8")).hexdigest()[:12].upper()
    return f"CTK-TRK-{digest}"


def _decode_samples(raw: bytes, sample_width: int) -> Iterable[float]:
    if sample_width == 1:
        for value in raw:
            yield (value - 128) / 128.0
    elif sample_width == 2:
        count = len(raw) // 2
        for value in struct.unpack(f"<{count}h", raw[: count * 2]):
            yield value / 32768.0
    elif sample_width == 3:
        for index in range(0, len(raw) - 2, 3):
            value = int.from_bytes(raw[index:index + 3], "little", signed=True)
            yield value / 8388608.0
    elif sample_width == 4:
        count = len(raw) // 4
        for value in struct.unpack(f"<{count}i", raw[: count * 4]):
            yield value / 2147483648.0
    else:
        raise ValueError(f"unsupported WAV sample width: {sample_width} bytes")


def analyze_audio_file(path: Path, root: Path | None = None) -> AudioAnalysis:
    path = path.expanduser().resolve()
    display_path = str(path.relative_to(root.resolve())) if root else str(path)
    if path.suffix.lower() not in SUPPORTED_AUDIO:
        return AudioAnalysis(
            track_id=_track_id(path), title=path.stem, path=display_path,
            format=path.suffix.lower().lstrip("."), duration_seconds=0.0,
            sample_rate=0, channels=0, sample_width_bits=0, peak=0.0, rms=0.0,
            energy=0.0, brightness=0.0, analysis_status="unsupported",
            analysis_notes="Install the optional music-analysis dependencies for this format.",
        )
    try:
        with wave.open(str(path), "rb") as handle:
            channels = handle.getnchannels()
            sample_rate = handle.getframerate()
            frames = handle.getnframes()
            sample_width = handle.getsampwidth()
            duration = frames / sample_rate if sample_rate else 0.0
            # Cap deterministic analysis to about 60 seconds to keep scans responsive.
            frames_to_read = min(frames, sample_rate * 60) if sample_rate else frames
            raw = handle.readframes(frames_to_read)
        samples = list(_decode_samples(raw, sample_width))
        if samples:
            peak = max(abs(value) for value in samples)
            rms = math.sqrt(sum(value * value for value in samples) / len(samples))
            zero_crossings = sum(1 for left, right in zip(samples, samples[1:]) if (left < 0 <= right) or (right < 0 <= left))
            brightness = min(1.0, zero_crossings / max(1, len(samples) - 1) * 12.0)
        else:
            peak = rms = brightness = 0.0
        energy = min(1.0, rms * 3.0)
        return AudioAnalysis(
            track_id=_track_id(path), title=path.stem, path=display_path,
            format=path.suffix.lower().lstrip("."), duration_seconds=duration,
            sample_rate=sample_rate, channels=channels,
            sample_width_bits=sample_width * 8, peak=peak, rms=rms,
            energy=energy, brightness=brightness,
            analysis_notes="Local deterministic WAV analysis; tempo and key are optional enrichment fields.",
        )
    except (wave.Error, EOFError, OSError, ValueError) as exc:
        return AudioAnalysis(
            track_id=_track_id(path), title=path.stem, path=display_path,
            format=path.suffix.lower().lstrip("."), duration_seconds=0.0,
            sample_rate=0, channels=0, sample_width_bits=0, peak=0.0, rms=0.0,
            energy=0.0, brightness=0.0, analysis_status="error",
            analysis_notes=str(exc),
        )


def analyze_folder(folder: Path, output: Path) -> list[AudioAnalysis]:
    folder = folder.expanduser().resolve()
    output = output.expanduser().resolve()
    analyses = [
        analyze_audio_file(path, folder)
        for path in sorted(folder.rglob("*"))
        if path.is_file() and path.suffix.lower() in {".wav", ".wave", ".mp3", ".flac", ".aiff", ".aif", ".m4a"}
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIO_ANALYSIS_COLUMNS)
        writer.writeheader()
        writer.writerows(item.to_row() for item in analyses)
    return analyses
