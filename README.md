# CallMeTK OS

CallMeTK OS is the command center for CallMeTK creative software projects.
It helps create, version, publish, release, and eventually automate projects like websites, AI music tools, education apps, and game prototypes.

## Version

Current version: **0.2.0**

## Install locally

From inside this folder:

```bash
python -m pip install -e .
```

Then test:

```bash
ctk --help
ctk doctor
```

Alternative:

```bash
python -m ctk --help
python -m ctk doctor
```

## Important

This is a Python project. Do not run `npm install` unless a future version includes a `package.json`.

## Commands

```bash
ctk doctor
ctk version
ctk new website ../my-website
ctk publish -m "Update project"
ctk release 0.2.1
```

## GitHub upload

Create an empty repository at:

```text
https://github.com/justcallmetk/callmetk-os
```

Then run:

```bash
git init
git add .
git commit -m "Initialize CallMeTK OS v0.2.0"
git branch -M main
git remote add origin https://github.com/justcallmetk/callmetk-os.git
git push -u origin main
```

## Roadmap

- v0.2: production-quality Python foundation
- v0.3: stronger project generator
- v0.4: GitHub automation
- v0.5: AI release notes and changelog assistant
- v1.0: stable public release
