# CallMeTK OS

CallMeTK OS is a developer and creator toolkit for building websites, AI apps, music release systems, educational tools, and games with clean naming, metadata, and CSV-first workflows.

## Version

v0.4.0 — Catalog Foundation

## Install locally

```bash
python -m pip install -e .
ctk doctor
```

## Common commands

```bash
ctk --help
ctk version
ctk doctor
```

Create projects:

```bash
ctk new website "CallMe TK Website" ../callmetk-website
ctk new music-release "Exotic Brown Pi 2" ../exotic-brown-pi-2
ctk new game "EBP Ninja" ../ebp-ninja
```

Naming and CSV:

```bash
ctk naming slug "Exotic Brown Pi 2"
ctk naming id music-release "Exotic Brown Pi 2"
ctk csv validate metadata.csv
```

Catalog and music:

```bash
ctk catalog init catalog.csv
ctk catalog add song "Exotic Brown Pi" --path assets/music/exotic-brown-pi.mp3 --tags "gritty;underground"
ctk music init data/music.csv
ctk music import ./assets/music data/music.csv --artist "CallMe TK"
```

## Philosophy

If we have to do it twice, CTK OS should automate it.

The AI recommends. The human approves.
