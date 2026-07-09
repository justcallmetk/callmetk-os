"""Naming utilities for CallMeTK OS.

The goal is simple: every project, asset, release, and export should have
clean names that are safe for folders, URLs, CSV rows, and future databases.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import re
import unicodedata

ALLOWED_TYPES = {
    "website": "WEB",
    "ai-app": "AIA",
    "music-release": "MUS",
    "education-app": "EDU",
    "education-tool": "EDU",
    "game": "GAM",
    "asset": "AST",
    "song": "SNG",
    "stem": "STM",
    "vocal": "VOC",
    "instrumental": "INS",
    "ep": "EP",
}

VALID_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VALID_ID_RE = re.compile(r"^CTK-[A-Z]{2,4}-\d{8}-[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(value: str) -> str:
    """Convert a name into a clean lowercase slug."""
    if not value or not value.strip():
        raise ValueError("Name cannot be empty.")
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text)
    ascii_text = re.sub(r"-+", "-", ascii_text).strip("-")
    if not ascii_text:
        raise ValueError("Name must contain at least one letter or number.")
    return ascii_text


def validate_slug(slug: str) -> bool:
    return bool(VALID_SLUG_RE.match(slug or ""))


def type_code(project_type: str) -> str:
    key = slugify(project_type)
    if key not in ALLOWED_TYPES:
        allowed = ", ".join(sorted(ALLOWED_TYPES))
        raise ValueError(f"Unknown type '{project_type}'. Allowed types: {allowed}")
    return ALLOWED_TYPES[key]


def ctk_id(project_type: str, name: str, created: date | None = None) -> str:
    """Create a stable CTK ID like CTK-MUS-20260709-exotic-brown-pi-2."""
    created = created or date.today()
    return f"CTK-{type_code(project_type)}-{created:%Y%m%d}-{slugify(name)}"


def validate_ctk_id(value: str) -> bool:
    return bool(VALID_ID_RE.match(value or ""))


@dataclass(frozen=True)
class NamingRecord:
    ctk_id: str
    name: str
    slug: str
    type: str
    created: str
    status: str = "draft"

    @classmethod
    def create(cls, project_type: str, name: str, created: date | None = None, status: str = "draft") -> "NamingRecord":
        created = created or date.today()
        return cls(
            ctk_id=ctk_id(project_type, name, created),
            name=name.strip(),
            slug=slugify(name),
            type=slugify(project_type),
            created=f"{created:%Y-%m-%d}",
            status=status,
        )
