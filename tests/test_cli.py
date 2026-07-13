from pathlib import Path

from ctk.cli import main
from ctk.catalog import MUSIC_COLUMNS, validate_required_csv
from ctk.csv_system import validate_csv
from ctk.naming import ctk_id, slugify, validate_ctk_id


def test_version_command(capsys):
    code = main(["version"])
    out = capsys.readouterr().out
    assert code == 0
    assert "0.7.0" in out


def test_help_command(capsys):
    code = main([])
    out = capsys.readouterr().out
    assert code == 0
    assert "CallMeTK OS" in out


def test_slugify():
    assert slugify("Exotic Brown Pi 2") == "exotic-brown-pi-2"
    assert slugify("CallMe TK: Website!") == "callme-tk-website"


def test_ctk_id():
    value = ctk_id("music-release", "Exotic Brown Pi 2")
    assert value.startswith("CTK-MUS-")
    assert value.endswith("-exotic-brown-pi-2")
    assert validate_ctk_id(value)


def test_csv_init_and_validate(tmp_path: Path):
    csv_path = tmp_path / "metadata.csv"
    code = main(["csv", "init", "music-release", "Exotic Brown Pi 2", str(csv_path)])
    assert code == 0
    assert csv_path.exists()
    assert validate_csv(csv_path) == []


def test_new_project_creates_metadata(tmp_path: Path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "VERSION").write_text("0.6.1\n")
    templates = repo / "templates" / "website"
    templates.mkdir(parents=True)
    (templates / "README.md").write_text("# {{PROJECT_NAME}}\n{{CTK_ID}}\n{{PROJECT_SLUG}}\n")
    monkeypatch.chdir(repo)
    dest = tmp_path / "site"
    code = main(["new", "website", "CallMe TK Website", str(dest)])
    assert code == 0
    assert (dest / "metadata.csv").exists()
    assert validate_csv(dest / "metadata.csv") == []
    assert "CallMe TK Website" in (dest / "README.md").read_text()


def test_catalog_add_and_validate(tmp_path: Path):
    catalog = tmp_path / "catalog.csv"
    code = main(["catalog", "init", str(catalog)])
    assert code == 0
    code = main(["catalog", "add", "song", "Exotic Brown Pi", "--catalog", str(catalog), "--tags", "gritty;underground"])
    assert code == 0
    code = main(["catalog", "validate", str(catalog)])
    assert code == 0
    text = catalog.read_text()
    assert "Exotic Brown Pi" in text


def test_music_import(tmp_path: Path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    (music_dir / "exotic-brown-pi.mp3").write_bytes(b"fake")
    output = tmp_path / "music.csv"
    code = main(["music", "import", str(music_dir), str(output), "--artist", "CallMe TK"])
    assert code == 0
    assert output.exists()
    assert "Exotic Brown Pi" in output.read_text()
    assert validate_required_csv(output, MUSIC_COLUMNS) == []


def test_game_init_data(tmp_path: Path):
    data = tmp_path / "data"
    code = main(["game", "init-data", str(data)])
    assert code == 0
    assert (data / "music.csv").exists()
    assert (data / "levels.csv").exists()
