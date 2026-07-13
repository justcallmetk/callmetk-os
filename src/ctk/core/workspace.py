from __future__ import annotations

import json
from pathlib import Path


def init_workspace(root: Path) -> Path:
    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    registry = root / "workspace.json"
    if not registry.exists():
        registry.write_text(json.dumps({"projects": [], "libraries": []}, indent=2) + "\n", encoding="utf-8")
    return registry


def workspace_status(root: Path) -> dict[str, int | str]:
    root = root.expanduser().resolve()
    registry = init_workspace(root)
    data = json.loads(registry.read_text(encoding="utf-8"))
    return {
        "path": str(root),
        "projects": len(data.get("projects", [])),
        "libraries": len(data.get("libraries", [])),
    }
