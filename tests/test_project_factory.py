from pathlib import Path
import pytest

from ctk.cli import main
from ctk.checks import check_project

TEMPLATES = ["website", "ai-app", "music-release", "education-app", "game"]

@pytest.mark.parametrize("template", TEMPLATES)
def test_all_project_templates_generate_complete_projects(tmp_path: Path, monkeypatch, template: str):
    source_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(source_root)
    destination = tmp_path / template
    assert main(["new", template, f"Test {template}", str(destination)]) == 0
    assert (destination / "metadata.csv").exists()
    assert (destination / "catalog.csv").exists()
    assert (destination / "project.yaml").exists()
    assert (destination / ".github/workflows/ci.yml").exists()
    assert check_project(destination) == []


def test_education_tool_alias_still_works(tmp_path: Path, monkeypatch):
    source_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(source_root)
    destination = tmp_path / "education"
    assert main(["new", "education-tool", "Legacy Education", str(destination)]) == 0
    assert 'type: "education-app"' in (destination / "project.yaml").read_text()


def test_check_command(tmp_path: Path, monkeypatch):
    source_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(source_root)
    destination = tmp_path / "website"
    assert main(["new", "website", "Checked Website", str(destination)]) == 0
    assert main(["check", str(destination)]) == 0
