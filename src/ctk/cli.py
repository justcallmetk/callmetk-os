from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from ctk import __version__
from ctk.csv_system import create_project_metadata, validate_csv
from ctk.naming import ctk_id, slugify, validate_ctk_id, validate_slug
from ctk.project_factory import SUPPORTED_TEMPLATES, create_project
from ctk.checks import capability_report, check_project
from ctk.catalog import (
    CATALOG_COLUMNS, MUSIC_COLUMNS, add_catalog_item, import_music_folder,
    init_catalog, init_game_data, init_music_csv, validate_required_csv,
)

ROOT_MARKERS = ("VERSION", "pyproject.toml", ".git")


def find_project_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for path in (current, *current.parents):
        if any((path / marker).exists() for marker in ROOT_MARKERS):
            return path
    return current


def run(cmd: list[str], cwd: Path | None = None) -> int:
    print("$ " + " ".join(cmd))
    completed = subprocess.run(cmd, cwd=str(cwd or Path.cwd()), check=False)
    return completed.returncode


def read_version(root: Path) -> str:
    version_file = root / "VERSION"
    if not version_file.exists():
        version_file.write_text(f"{__version__}\n", encoding="utf-8")
    return version_file.read_text(encoding="utf-8").strip()


def doctor(_: argparse.Namespace) -> int:
    root = find_project_root()
    print("CallMeTK OS Doctor")
    print(f"Version: {__version__}")
    print(f"Project root: {root}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Executable: {sys.executable}")
    print(f"Git: {'found' if shutil.which('git') else 'missing'}")
    print(f"VERSION file: {read_version(root)}")
    if (root / "package.json").exists():
        print("Node project: package.json found")
    else:
        print("Node project: no package.json found. Use Python commands for CTK OS.")
    metadata = root / "metadata.csv"
    if metadata.exists():
        errors = validate_csv(metadata)
        print("metadata.csv: valid" if not errors else f"metadata.csv: {len(errors)} issue(s)")
    else:
        print("metadata.csv: not found yet")
    if not (root / ".git").exists():
        print("Warning: this folder is not a Git repository yet. Run: git init")
    return 0


def version(_: argparse.Namespace) -> int:
    print(__version__)
    return 0


def new_project(args: argparse.Namespace) -> int:
    root = find_project_root()
    destination = Path(args.path or slugify(args.name)).resolve()
    try:
        row = create_project(root, args.template, args.name, destination)
    except FileNotFoundError:
        print(f"Template not found: {args.template}")
        print("Available templates:")
        for item in SUPPORTED_TEMPLATES:
            print(f"- {item}")
        return 1
    except FileExistsError as exc:
        print(str(exc))
        return 1
    print(f"Created {args.template} project at {destination}")
    print(f"CTK ID: {row['ctk_id']}")
    print(f"Metadata: {destination / 'metadata.csv'}")
    print(f"Project config: {destination / 'project.yaml'}")
    return 0


def naming_slug(args: argparse.Namespace) -> int:
    print(slugify(args.name))
    return 0


def naming_id(args: argparse.Namespace) -> int:
    print(ctk_id(args.type, args.name))
    return 0


def naming_validate(args: argparse.Namespace) -> int:
    value = args.value
    if validate_ctk_id(value):
        print("valid ctk_id")
        return 0
    if validate_slug(value):
        print("valid slug")
        return 0
    print("invalid name/id format")
    return 1


def csv_init(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    row = create_project_metadata(path, args.type, args.name)
    print(f"Created CSV: {path}")
    print(f"CTK ID: {row['ctk_id']}")
    return 0


def csv_validate(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    errors = validate_csv(path)
    if not errors:
        print(f"CSV valid: {path}")
        return 0
    print(f"CSV has {len(errors)} issue(s):")
    for error in errors:
        print(f"- {error}")
    return 1



def catalog_init(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    init_catalog(path)
    print(f"Created catalog CSV: {path}")
    return 0


def catalog_add(args: argparse.Namespace) -> int:
    path = Path(args.catalog).resolve()
    row = add_catalog_item(path, args.type, args.name, args.source_path or "", args.tags or "", args.notes or "")
    print(f"Added catalog item: {row['name']}")
    print(f"CTK ID: {row['ctk_id']}")
    print(f"Catalog: {path}")
    return 0


def catalog_validate(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    errors = validate_required_csv(path, CATALOG_COLUMNS)
    if not errors:
        print(f"Catalog CSV valid: {path}")
        return 0
    print(f"Catalog CSV has {len(errors)} issue(s):")
    for error in errors:
        print(f"- {error}")
    return 1


def music_init(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    init_music_csv(path)
    print(f"Created music CSV: {path}")
    return 0


def music_import(args: argparse.Namespace) -> int:
    folder = Path(args.folder).resolve()
    output = Path(args.output).resolve()
    if not folder.exists():
        print(f"Music folder not found: {folder}")
        return 1
    count = import_music_folder(folder, output, args.artist)
    print(f"Imported {count} audio file(s) into {output}")
    return 0


def music_validate(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    errors = validate_required_csv(path, MUSIC_COLUMNS)
    if not errors:
        print(f"Music CSV valid: {path}")
        return 0
    print(f"Music CSV has {len(errors)} issue(s):")
    for error in errors:
        print(f"- {error}")
    return 1


def game_init_data(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).resolve()
    init_game_data(data_dir)
    print(f"Created game data CSVs in: {data_dir}")
    return 0


def check_command(args: argparse.Namespace) -> int:
    root = Path(args.path).resolve() if args.path else find_project_root()
    print(f"CallMeTK OS Check: {root}")
    for line in capability_report(root):
        print(line)
    errors = check_project(root)
    if errors:
        print(f"Check failed with {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Project structure and CSV files are valid.")
    return 0

def publish(args: argparse.Namespace) -> int:
    root = find_project_root()
    message = args.message or f"Publish v{read_version(root)}"
    if run(["git", "status", "--short"], cwd=root) != 0:
        print("Git is not ready. Is this a repository?")
        return 1
    steps = [["git", "add", "."], ["git", "commit", "-m", message], ["git", "push"]]
    for step in steps:
        code = run(step, cwd=root)
        if code != 0:
            print("Publish stopped. Fix the message above, then run again.")
            return code
    return 0


def release(args: argparse.Namespace) -> int:
    root = find_project_root()
    new_version = args.version
    (root / "VERSION").write_text(f"{new_version}\n", encoding="utf-8")
    changelog = root / "CHANGELOG.md"
    entry = f"\n## v{new_version}\n\n- Release v{new_version}.\n"
    if changelog.exists():
        changelog.write_text(changelog.read_text(encoding="utf-8") + entry, encoding="utf-8")
    else:
        changelog.write_text(f"# Changelog\n{entry}", encoding="utf-8")
    if run(["git", "add", "."], cwd=root) != 0:
        return 1
    if run(["git", "commit", "-m", f"Release v{new_version}"], cwd=root) != 0:
        return 1
    if run(["git", "tag", f"v{new_version}"], cwd=root) != 0:
        return 1
    return run(["git", "push", "origin", "main", "--tags"], cwd=root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ctk", description="CallMeTK OS developer toolkit")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("doctor", help="Check your local setup")
    p.set_defaults(func=doctor)

    p = sub.add_parser("version", help="Show CTK OS version")
    p.set_defaults(func=version)

    p = sub.add_parser("new", help="Create a project from a template")
    p.add_argument("template", help="Template name: website, ai-app, music-release, education-app, or game")
    p.add_argument("name", help="Human project name, e.g. Exotic Brown Pi 2")
    p.add_argument("path", nargs="?", help="Optional destination folder. Defaults to slugified name.")
    p.set_defaults(func=new_project)

    p = sub.add_parser("naming", help="Naming tools for slugs and CTK IDs")
    naming_sub = p.add_subparsers(dest="naming_command")
    p_slug = naming_sub.add_parser("slug", help="Create a clean slug")
    p_slug.add_argument("name")
    p_slug.set_defaults(func=naming_slug)
    p_id = naming_sub.add_parser("id", help="Create a CTK ID")
    p_id.add_argument("type")
    p_id.add_argument("name")
    p_id.set_defaults(func=naming_id)
    p_val = naming_sub.add_parser("validate", help="Validate a slug or CTK ID")
    p_val.add_argument("value")
    p_val.set_defaults(func=naming_validate)

    p = sub.add_parser("csv", help="CSV metadata tools")
    csv_sub = p.add_subparsers(dest="csv_command")
    p_init = csv_sub.add_parser("init", help="Create a metadata CSV")
    p_init.add_argument("type")
    p_init.add_argument("name")
    p_init.add_argument("path", nargs="?", default="metadata.csv")
    p_init.set_defaults(func=csv_init)
    p_check = csv_sub.add_parser("validate", help="Validate a metadata CSV")
    p_check.add_argument("path", nargs="?", default="metadata.csv")
    p_check.set_defaults(func=csv_validate)


    p = sub.add_parser("catalog", help="Creative catalog tools")
    catalog_sub = p.add_subparsers(dest="catalog_command")
    p_cat_init = catalog_sub.add_parser("init", help="Create a catalog CSV")
    p_cat_init.add_argument("path", nargs="?", default="catalog.csv")
    p_cat_init.set_defaults(func=catalog_init)
    p_cat_add = catalog_sub.add_parser("add", help="Add an item to a catalog CSV")
    p_cat_add.add_argument("type", help="Item type, e.g. song, album, photo, video, merch, game")
    p_cat_add.add_argument("name", help="Human-readable item name")
    p_cat_add.add_argument("--catalog", default="catalog.csv", help="Catalog CSV path")
    p_cat_add.add_argument("--path", dest="source_path", default="", help="Source asset path")
    p_cat_add.add_argument("--tags", default="", help="Semicolon-separated tags")
    p_cat_add.add_argument("--notes", default="", help="Optional notes")
    p_cat_add.set_defaults(func=catalog_add)
    p_cat_val = catalog_sub.add_parser("validate", help="Validate a catalog CSV")
    p_cat_val.add_argument("path", nargs="?", default="catalog.csv")
    p_cat_val.set_defaults(func=catalog_validate)

    p = sub.add_parser("music", help="Music catalog tools")
    music_sub = p.add_subparsers(dest="music_command")
    p_music_init = music_sub.add_parser("init", help="Create a music CSV")
    p_music_init.add_argument("path", nargs="?", default="data/music.csv")
    p_music_init.set_defaults(func=music_init)
    p_music_import = music_sub.add_parser("import", help="Import a folder of audio files into music.csv")
    p_music_import.add_argument("folder", help="Folder containing audio files")
    p_music_import.add_argument("output", nargs="?", default="data/music.csv", help="Output music CSV")
    p_music_import.add_argument("--artist", default="CallMe TK", help="Artist name for imported tracks")
    p_music_import.set_defaults(func=music_import)
    p_music_val = music_sub.add_parser("validate", help="Validate a music CSV")
    p_music_val.add_argument("path", nargs="?", default="data/music.csv")
    p_music_val.set_defaults(func=music_validate)

    p = sub.add_parser("game", help="Game project tools")
    game_sub = p.add_subparsers(dest="game_command")
    p_game_data = game_sub.add_parser("init-data", help="Create game data CSVs")
    p_game_data.add_argument("data_dir", nargs="?", default="data")
    p_game_data.set_defaults(func=game_init_data)

    p = sub.add_parser("check", help="Validate project structure, metadata, and capabilities")
    p.add_argument("path", nargs="?", help="Project path. Defaults to current project root.")
    p.set_defaults(func=check_command)

    p = sub.add_parser("publish", help="Commit and push current project")
    p.add_argument("-m", "--message", help="Commit message")
    p.set_defaults(func=publish)

    p = sub.add_parser("release", help="Bump VERSION, update changelog, tag, and push")
    p.add_argument("version", help="New version, e.g. 0.3.1")
    p.set_defaults(func=release)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)
