from __future__ import annotations

import csv
import shutil
from datetime import date
from pathlib import Path

from .catalog import CATALOG_COLUMNS, write_csv
from .csv_system import create_project_metadata
from .naming import slugify

TEMPLATE_ALIASES = {"education-app": "education-tool"}
SUPPORTED_TEMPLATES = ("website", "ai-app", "music-release", "education-app", "education-tool", "game")


def canonical_template(name: str) -> str:
    return TEMPLATE_ALIASES.get(name, name)


def project_type(name: str) -> str:
    return "education-app" if name in {"education-app", "education-tool"} else name


def render_text_files(destination: Path, values: dict[str, str]) -> None:
    for path in destination.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".wav", ".mp3"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for key, value in values.items():
            text = text.replace("{{" + key + "}}", value)
        path.write_text(text, encoding="utf-8")


def write_project_yaml(path: Path, *, name: str, slug: str, ctk_id: str, kind: str) -> None:
    path.write_text(
        "\n".join([
            f'name: "{name}"',
            f'slug: "{slug}"',
            f'ctk_id: "{ctk_id}"',
            f'type: "{kind}"',
            f'created: "{date.today():%Y-%m-%d}"',
            'status: "draft"',
            'ctk_os_version: "0.5.0"',
            "ai_manager:",
            "  enabled: false",
            "toast:",
            "  approval_required: true",
            "  auto_accept: false",
            "",
        ]),
        encoding="utf-8",
    )


def write_ci(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """name: CI\n\non:\n  push:\n  pull_request:\n\njobs:\n  validate:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - name: Verify project files\n        run: |\n          test -f VERSION\n          test -f metadata.csv\n          test -f catalog.csv\n          test -f project.yaml\n""",
        encoding="utf-8",
    )


def create_project(repo_root: Path, template_name: str, name: str, destination: Path) -> dict[str, str]:
    requested = slugify(template_name)
    canonical = canonical_template(requested)
    template = repo_root / "templates" / canonical
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")

    shutil.copytree(template, destination)
    kind = project_type(requested)
    project_slug = slugify(name)
    row = create_project_metadata(destination / "metadata.csv", kind, name)
    write_csv(destination / "catalog.csv", CATALOG_COLUMNS, [])
    write_project_yaml(destination / "project.yaml", name=name.strip(), slug=project_slug, ctk_id=row["ctk_id"], kind=kind)
    write_ci(destination / ".github" / "workflows" / "ci.yml")

    values = {
        "PROJECT_NAME": name.strip(),
        "PROJECT_SLUG": project_slug,
        "CTK_ID": row["ctk_id"],
        "PROJECT_TYPE": kind,
    }
    render_text_files(destination, values)
    return row
