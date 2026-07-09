from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from ctk import __version__

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
    if not (root / ".git").exists():
        print("Warning: this folder is not a Git repository yet. Run: git init")
    return 0


def version(_: argparse.Namespace) -> int:
    print(__version__)
    return 0


def new_project(args: argparse.Namespace) -> int:
    root = find_project_root()
    template = root / "templates" / args.template
    destination = Path(args.name).resolve()
    if not template.exists():
        print(f"Template not found: {args.template}")
        print("Available templates:")
        templates_dir = root / "templates"
        if templates_dir.exists():
            for item in sorted(p.name for p in templates_dir.iterdir() if p.is_dir()):
                print(f"- {item}")
        return 1
    if destination.exists():
        print(f"Destination already exists: {destination}")
        return 1
    shutil.copytree(template, destination)
    print(f"Created {args.template} project at {destination}")
    return 0


def publish(args: argparse.Namespace) -> int:
    root = find_project_root()
    message = args.message or f"Publish v{read_version(root)}"
    if run(["git", "status", "--short"], cwd=root) != 0:
        print("Git is not ready. Is this a repository?")
        return 1
    steps = [
        ["git", "add", "."],
        ["git", "commit", "-m", message],
        ["git", "push"],
    ]
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
    p.add_argument("template", help="Template name, e.g. website, ai-app, music-release")
    p.add_argument("name", help="Destination folder")
    p.set_defaults(func=new_project)

    p = sub.add_parser("publish", help="Commit and push current project")
    p.add_argument("-m", "--message", help="Commit message")
    p.set_defaults(func=publish)

    p = sub.add_parser("release", help="Bump VERSION, update changelog, tag, and push")
    p.add_argument("version", help="New version, e.g. 0.2.1")
    p.set_defaults(func=release)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 0
    return args.func(args)
