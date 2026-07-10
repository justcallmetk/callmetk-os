from __future__ import annotations

import csv
import shutil
from pathlib import Path

from .catalog import CATALOG_COLUMNS, validate_required_csv
from .csv_system import validate_csv

REQUIRED_PROJECT_FILES = ["VERSION", "README.md", "metadata.csv", "catalog.csv", "project.yaml"]


def check_project(root: Path) -> list[str]:
    errors: list[str] = []
    for filename in REQUIRED_PROJECT_FILES:
        if not (root / filename).exists():
            errors.append(f"Missing required file: {filename}")
    if (root / "metadata.csv").exists():
        errors.extend(validate_csv(root / "metadata.csv"))
    if (root / "catalog.csv").exists():
        errors.extend(validate_required_csv(root / "catalog.csv", CATALOG_COLUMNS))
    project_yaml = root / "project.yaml"
    if project_yaml.exists():
        text = project_yaml.read_text(encoding="utf-8")
        for key in ("name:", "slug:", "ctk_id:", "type:"):
            if key not in text:
                errors.append(f"project.yaml missing key: {key[:-1]}")
    return errors


def capability_report(root: Path) -> list[str]:
    return [
        f"Git: {'found' if shutil.which('git') else 'missing'}",
        f"Pytest: {'found' if shutil.which('pytest') else 'missing'}",
        f"Snyk CLI: {'found' if shutil.which('snyk') else 'not installed (GitHub app may still monitor remotely)'}",
        f"Git repository: {'yes' if (root / '.git').exists() else 'no'}",
    ]
