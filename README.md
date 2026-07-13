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

## CTK Core v0.6.1

Configure zero-cost AI routing by default:

```bash
ctk ai init
ctk ai mode free
ctk ai status
ctk ai route coding
```

Create and index a Creative Library outside Git:

```bash
ctk library init ~/CallMeTK/callmetk-library
ctk library scan ~/CallMeTK/callmetk-library
ctk library validate
```

Create the first CTK Workspace registry:

```bash
ctk workspace init ~/CallMeTK/workspace
ctk workspace status
```

See `docs/CTK_CORE.md` for the v0.6 architecture and commands.

## Philosophy and governance

CallMeTK OS preserves creator control through local-first processing, explainable recommendations, category-based calibration, and human approval by default.

Start with:

- `docs/architecture/CTK_OS_CONSTITUTION.md`
- `docs/architecture/TOAST_AI_STANDARD.md`
- `docs/governance/GIT_CONTENT_POLICY.md`

## v0.7 Music Intelligence

CallMeTK OS now includes a free, local-first music pipeline:

```bash
ctk music analyze ~/CallMeTK/callmetk-library/music/masters data/audio-analysis.csv
ctk music cluster data/audio-analysis.csv data/music-clusters.csv --clusters 3
ctk music ep-build data/music-clusters.csv --tracks 4
ctk music dna data/audio-analysis.csv
```

Core WAV analysis uses the Python standard library. Richer future analysis can be installed with `python -m pip install -e '.[music]'`. Raw masters remain outside Git; structured analysis and TOAST recommendations can be versioned safely.
