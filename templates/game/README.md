# {{PROJECT_NAME}}

CTK ID: `{{CTK_ID}}`
Slug: `{{PROJECT_SLUG}}`

This game project is catalog-driven. Add music to `assets/music/`, then run:

```bash
ctk music import assets/music data/music.csv --artist "CallMe TK"
ctk music validate data/music.csv
```

Use `data/levels.csv` to assign songs to levels through `bgm_track_id`.

## Structure

- `assets/music/` — songs, loops, instrumentals, boss themes
- `data/music.csv` — track metadata for the game
- `data/levels.csv` — levels that can reference tracks
- `data/catalog.csv` — related creative objects
- `game.yaml` — project settings
