# CTK OS Catalog System

CTK OS v0.4 introduces a CSV-first creative catalog.

The catalog connects songs, albums, beats, stems, photos, videos, merch, games, lessons, and website content with stable CTK IDs.

## Core idea

Every reusable creative object gets:

- `ctk_id`
- `name`
- `slug`
- `type`
- `status`
- `source_path`
- `related_to`
- `tags`
- `notes`

Example:

```csv
ctk_id,name,slug,type,status,source_path,related_to,tags,notes
CTK-SON-20260709-exotic-brown-pi,Exotic Brown Pi,exotic-brown-pi,song,draft,assets/music/exotic-brown-pi.mp3,,gritty;underground,Imported by CTK OS
```

## Commands

Create a catalog:

```bash
ctk catalog init catalog.csv
```

Add an item:

```bash
ctk catalog add song "Exotic Brown Pi" --path assets/music/exotic-brown-pi.mp3 --tags "gritty;underground"
```

Validate:

```bash
ctk catalog validate catalog.csv
```

## Music for games

Create an empty music CSV:

```bash
ctk music init data/music.csv
```

Import a folder of songs:

```bash
ctk music import ./assets/music data/music.csv --artist "CallMe TK"
```

Game levels can reference tracks by `track_id`:

```csv
level_id,name,type,difficulty,bgm_track_id,notes
LV001,Subway,level,easy,MUS001,Opening level
```

## Human approval first

The CSV system is designed for the TOAST workflow: AI can recommend tags, use cases, moods, energy, or EP groupings, but the human approves changes before release.
