# Troubleshooting

## `npm install` fails with missing package.json

CallMeTK OS v0.2.0 is a Python project, not a Node project. Use:

```bash
python -m pip install -e .
```

## `ctk: command not found`

Activate your virtual environment and reinstall:

```bash
source .venv/bin/activate
python -m pip install -e .
```

Then try:

```bash
ctk --help
python -m ctk --help
```

## GitHub says repository not found

Create the GitHub repo first. Use the exact name:

```text
callmetk-os
```

Do not add README, license, or gitignore on GitHub if your local repo already has them.
