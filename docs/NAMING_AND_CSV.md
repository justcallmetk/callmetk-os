# Naming and CSV System

CallMeTK OS v0.3.0 introduces a consistent naming and metadata system.

## Naming rule

Every generated project receives:

```text
CTK-<TYPE>-<YYYYMMDD>-<slug>
```

Example:

```text
CTK-MUS-20260709-exotic-brown-pi-2
```

## Supported type codes

| Type | Code |
|---|---|
| website | WEB |
| ai-app | AIA |
| music-release | MUS |
| education-tool / education-app | EDU |
| game | GAM |
| asset | AST |
| song | SNG |
| stem | STM |
| vocal | VOC |
| instrumental | INS |
| ep | EP |

## CSV columns

`metadata.csv` uses these columns:

```text
ctk_id,name,slug,type,created,status,source_path,tags,notes
```

Required columns:

```text
ctk_id,name,slug,type,created,status
```

## Commands

```bash
ctk naming slug "Exotic Brown Pi 2"
ctk naming id music-release "Exotic Brown Pi 2"
ctk naming validate CTK-MUS-20260709-exotic-brown-pi-2

ctk csv init music-release "Exotic Brown Pi 2"
ctk csv validate metadata.csv
```

## Why this matters

This makes every CTK project easier to search, organize, import, export, and connect to AI tools later.
