from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from ctk import __version__
from ctk.csv_system import create_project_metadata, validate_csv
from ctk.naming import ctk_id, slugify, validate_ctk_id, validate_slug
from ctk.project_factory import SUPPORTED_TEMPLATES, create_project
from ctk.core.ai_manager import recommend_provider
from ctk.core.config import VALID_COST_MODES, default_config_path, load_config, save_config
from ctk.core.library import init_library, scan_library, validate_library
from ctk.core.providers import PROVIDER_CAPABILITIES
from ctk.core.workspace import init_workspace, workspace_status
from ctk.music.analyzer import analyze_folder
from ctk.music.cluster import cluster_tracks
from ctk.music.dna import build_creative_dna
from ctk.music.ep_builder import build_ep_recommendation
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


def music_analyze(args: argparse.Namespace) -> int:
    folder = Path(args.folder).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not folder.exists():
        print(f"Audio folder not found: {folder}")
        return 1
    analyses = analyze_folder(folder, output)
    complete = sum(item.analysis_status == "complete" for item in analyses)
    unsupported = sum(item.analysis_status == "unsupported" for item in analyses)
    failed = sum(item.analysis_status == "error" for item in analyses)
    print(f"Analyzed {len(analyses)} audio file(s)")
    print(f"Complete: {complete}; optional enrichment needed: {unsupported}; errors: {failed}")
    print(f"Analysis CSV: {output}")
    return 0 if failed == 0 else 1


def music_cluster(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    if not input_path.exists():
        print(f"Analysis CSV not found: {input_path}")
        return 1
    try:
        result = cluster_tracks(input_path, output_path, args.clusters, args.seed)
    except ValueError as exc:
        print(str(exc))
        return 1
    print(f"Clustered {len(result.assignments)} track(s) into {result.clusters} cluster(s)")
    print(f"Inertia: {result.inertia:.4f}")
    print(f"Cluster CSV: {output_path}")
    return 0


def music_ep_build(args: argparse.Namespace) -> int:
    cluster_path = Path(args.clusters_csv).expanduser().resolve()
    if not cluster_path.exists():
        print(f"Cluster CSV not found: {cluster_path}")
        return 1
    try:
        decision = build_ep_recommendation(cluster_path, args.tracks, args.cluster_id)
    except ValueError as exc:
        print(str(exc))
        return 1
    errors = decision.validate()
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print(json.dumps(decision.to_dict(), indent=2))
    return 0


def music_dna(args: argparse.Namespace) -> int:
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"Analysis CSV not found: {input_path}")
        return 1
    print(json.dumps(build_creative_dna(input_path), indent=2))
    return 0


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

def ai_init(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve() if args.path else default_config_path()
    config = load_config(path)
    saved = save_config(config, path)
    print(f"Created CTK AI config: {saved}")
    print("Cost mode: free")
    print("Paid fallback: disabled")
    return 0


def ai_mode(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve() if args.path else default_config_path()
    config = load_config(path)
    config.ai.cost_mode = args.mode
    if args.mode == "free":
        config.ai.allow_paid_fallback = False
        config.ai.monthly_budget_usd = 0.0
    elif args.budget is not None:
        config.ai.monthly_budget_usd = max(0.0, args.budget)
    save_config(config, path)
    print(f"AI cost mode set to: {args.mode}")
    print(f"Monthly budget: ${config.ai.monthly_budget_usd:.2f}")
    print(f"Paid fallback: {'enabled' if config.ai.allow_paid_fallback else 'disabled'}")
    return 0


def ai_status(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve() if args.path else default_config_path()
    config = load_config(path)
    print("CTK AI Status")
    print(f"Config: {path}")
    print(f"Cost mode: {config.ai.cost_mode}")
    print(f"Monthly budget: ${config.ai.monthly_budget_usd:.2f}")
    print(f"Paid fallback: {'enabled' if config.ai.allow_paid_fallback else 'disabled'}")
    print(f"Cost approval: {'required' if config.ai.require_cost_approval else 'not required'}")
    for name, provider in config.ai.providers.items():
        state = "enabled" if provider.enabled else "disabled"
        print(f"- {name}: {state}; model={provider.model or 'not set'}")
    return 0


def ai_providers(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve() if args.path else default_config_path()
    config = load_config(path)
    print("CTK AI Providers")
    for name, capability in PROVIDER_CAPABILITIES.items():
        provider = config.ai.providers.get(name)
        state = "enabled" if provider and provider.enabled else "disabled"
        cost = "free/local capable" if capability.can_be_free or capability.is_local else "paid"
        print(f"- {name}: {state}; {cost}")
    return 0


def ai_route(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve() if args.path else default_config_path()
    config = load_config(path)
    costs = {args.provider: args.estimated_cost} if args.provider else {}
    if args.provider and args.provider in config.ai.providers:
        config.ai.providers[args.provider].enabled = True
    decision = recommend_provider(config, args.task, costs)
    errors = decision.validate()
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print(json.dumps(decision.to_dict(), indent=2))
    return 0


def library_init_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    catalog = init_library(root)
    config = load_config()
    config.library_path = str(root)
    save_config(config)
    print(f"Created CTK Creative Library: {root}")
    print(f"Catalog: {catalog}")
    return 0


def library_scan_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    result = scan_library(root)
    print(f"Scanned {result.scanned} file(s)")
    print(f"Indexed {result.indexed} asset(s)")
    print(f"Catalog: {result.catalog_path}")
    return 0


def library_status_command(args: argparse.Namespace) -> int:
    config = load_config()
    raw = args.path or config.library_path
    if not raw:
        print("No Creative Library configured. Run: ctk library init <path>")
        return 1
    root = Path(raw).expanduser().resolve()
    catalog = root / "catalog" / "library.csv"
    rows = 0
    if catalog.exists():
        import csv
        with catalog.open(newline="", encoding="utf-8") as handle:
            rows = sum(1 for _ in csv.DictReader(handle))
    print("CTK Creative Library")
    print(f"Path: {root}")
    print(f"Catalog: {catalog}")
    print(f"Indexed assets: {rows}")
    return 0


def library_validate_command(args: argparse.Namespace) -> int:
    config = load_config()
    raw = args.path or config.library_path
    if not raw:
        print("No Creative Library configured.")
        return 1
    errors = validate_library(Path(raw))
    if errors:
        print(f"Library validation failed with {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Creative Library is valid.")
    return 0


def workspace_init_command(args: argparse.Namespace) -> int:
    root = Path(args.path).expanduser().resolve()
    registry = init_workspace(root)
    config = load_config()
    config.workspace_path = str(root)
    save_config(config)
    print(f"Created CTK Workspace: {root}")
    print(f"Registry: {registry}")
    return 0


def workspace_status_command(args: argparse.Namespace) -> int:
    config = load_config()
    raw = args.path or config.workspace_path
    if not raw:
        print("No workspace configured. Run: ctk workspace init <path>")
        return 1
    status = workspace_status(Path(raw))
    print("CTK Workspace")
    print(f"Path: {status['path']}")
    print(f"Projects: {status['projects']}")
    print(f"Libraries: {status['libraries']}")
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
    p_music_analyze = music_sub.add_parser("analyze", help="Extract local audio features into a CSV")
    p_music_analyze.add_argument("folder", help="Folder containing audio files")
    p_music_analyze.add_argument("output", nargs="?", default="data/audio-analysis.csv")
    p_music_analyze.set_defaults(func=music_analyze)
    p_music_cluster = music_sub.add_parser("cluster", help="Group analyzed tracks using local K-Means")
    p_music_cluster.add_argument("input", nargs="?", default="data/audio-analysis.csv")
    p_music_cluster.add_argument("output", nargs="?", default="data/music-clusters.csv")
    p_music_cluster.add_argument("--clusters", type=int, default=3)
    p_music_cluster.add_argument("--seed", type=int, default=7)
    p_music_cluster.set_defaults(func=music_cluster)
    p_music_ep = music_sub.add_parser("ep-build", help="Create a TOAST mini-EP recommendation")
    p_music_ep.add_argument("clusters_csv", nargs="?", default="data/music-clusters.csv")
    p_music_ep.add_argument("--tracks", type=int, default=4)
    p_music_ep.add_argument("--cluster-id", type=int)
    p_music_ep.set_defaults(func=music_ep_build)
    p_music_dna = music_sub.add_parser("dna", help="Summarize the catalog's Creative DNA")
    p_music_dna.add_argument("input", nargs="?", default="data/audio-analysis.csv")
    p_music_dna.set_defaults(func=music_dna)

    p = sub.add_parser("game", help="Game project tools")
    game_sub = p.add_subparsers(dest="game_command")
    p_game_data = game_sub.add_parser("init-data", help="Create game data CSVs")
    p_game_data.add_argument("data_dir", nargs="?", default="data")
    p_game_data.set_defaults(func=game_init_data)

    p = sub.add_parser("check", help="Validate project structure, metadata, and capabilities")
    p.add_argument("path", nargs="?", help="Project path. Defaults to current project root.")
    p.set_defaults(func=check_command)


    p = sub.add_parser("ai", help="AI configuration, cost controls, and provider routing")
    ai_sub = p.add_subparsers(dest="ai_command")
    p_ai_init = ai_sub.add_parser("init", help="Create the CTK AI configuration")
    p_ai_init.add_argument("--path", help="Optional config path")
    p_ai_init.set_defaults(func=ai_init)
    p_ai_mode = ai_sub.add_parser("mode", help="Set free, balanced, or quality mode")
    p_ai_mode.add_argument("mode", choices=sorted(VALID_COST_MODES))
    p_ai_mode.add_argument("--budget", type=float, help="Monthly budget in USD")
    p_ai_mode.add_argument("--path", help="Optional config path")
    p_ai_mode.set_defaults(func=ai_mode)
    p_ai_status = ai_sub.add_parser("status", help="Show AI cost and provider settings")
    p_ai_status.add_argument("--path", help="Optional config path")
    p_ai_status.set_defaults(func=ai_status)
    p_ai_providers = ai_sub.add_parser("providers", help="List supported AI providers")
    p_ai_providers.add_argument("--path", help="Optional config path")
    p_ai_providers.set_defaults(func=ai_providers)
    p_ai_route = ai_sub.add_parser("route", help="Create a TOAST provider recommendation")
    p_ai_route.add_argument("task", help="Task type, e.g. coding, caption, vision")
    p_ai_route.add_argument("--provider", choices=sorted(PROVIDER_CAPABILITIES), help="Temporarily enable a provider")
    p_ai_route.add_argument("--estimated-cost", type=float, default=0.0)
    p_ai_route.add_argument("--path", help="Optional config path")
    p_ai_route.set_defaults(func=ai_route)

    p = sub.add_parser("library", help="Creative Library tools")
    library_sub = p.add_subparsers(dest="library_command")
    p_library_init = library_sub.add_parser("init", help="Create a Creative Library")
    p_library_init.add_argument("path")
    p_library_init.set_defaults(func=library_init_command)
    p_library_scan = library_sub.add_parser("scan", help="Index Creative Library assets")
    p_library_scan.add_argument("path")
    p_library_scan.set_defaults(func=library_scan_command)
    p_library_status = library_sub.add_parser("status", help="Show Creative Library status")
    p_library_status.add_argument("path", nargs="?")
    p_library_status.set_defaults(func=library_status_command)
    p_library_validate = library_sub.add_parser("validate", help="Validate Creative Library metadata")
    p_library_validate.add_argument("path", nargs="?")
    p_library_validate.set_defaults(func=library_validate_command)

    p = sub.add_parser("workspace", help="CTK Workspace tools")
    workspace_sub = p.add_subparsers(dest="workspace_command")
    p_workspace_init = workspace_sub.add_parser("init", help="Create a CTK Workspace")
    p_workspace_init.add_argument("path")
    p_workspace_init.set_defaults(func=workspace_init_command)
    p_workspace_status = workspace_sub.add_parser("status", help="Show CTK Workspace status")
    p_workspace_status.add_argument("path", nargs="?")
    p_workspace_status.set_defaults(func=workspace_status_command)

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
