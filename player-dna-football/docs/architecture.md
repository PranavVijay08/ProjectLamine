# Architecture

## Overview

Project Lamine is split into a Next.js frontend and a FastAPI backend. The MVP uses a local CSV dataset so the product can be tested before connecting to a production data source.

## Backend

FastAPI exposes four core endpoints:

- `GET /players`
- `GET /players/{player_id}`
- `GET /players/{player_id}/similar`
- `GET /players/{player_id}/compare/{other_player_id}`

The backend loads player data through `app/utils/data_loader.py`. It prefers `data/processed/player_current_profiles.csv`, supports `PLAYER_DNA_DATA_PATH` for local overrides, and falls back to `data/players_mock.csv`.

Similarity logic lives in `app/services/similarity_service.py`, while explanation text lives in `app/services/explanation_service.py`.

## Data Ingestion

Ingestion code lives in `backend/app/ingestion`.

- `sources/football_data_org.py` fetches Top 5 league roster context through the football-data.org API.
- `sources/statsbomb_open.py` fetches StatsBomb Open Data JSON and derives event-based player profile metrics for selected open competitions.
- `builders.py` coordinates raw snapshot saving and processed CSV output.
- `scripts/update_dataset.py` is the local PowerShell-friendly command-line entry point.

The data directory is organised as:

```text
data/
  raw/
    football_data_org/
    statsbomb_open/
  processed/
    player_current_profiles.csv
  reference/
    league_codes.json
    source_registry.json
```

football-data.org is used for player identity, club and league context. StatsBomb Open Data is used for event-derived metric development. Future paid providers should target the same processed profile schema so the API does not need to change.

## Similarity Pipeline

1. Load validated player rows from the active processed CSV or mock fallback.
2. Select numerical playing-style attributes.
3. Fit `StandardScaler` on the dataset.
4. Compute cosine similarity between the selected player and every other player.
5. Convert cosine similarity to a `0-100` percentage.
6. Exclude the selected player.
7. Apply optional filters.
8. Return the top 10 matches with a short explanation.

## Frontend

The frontend uses the Next.js App Router:

- `/` dashboard homepage
- `/players` search page
- `/players/[id]` profile page
- `/players/[id]/similar` similarity results and comparison page

Reusable components are in `frontend/components`. Data access is centralised in `frontend/lib/api.ts`.

## Future Database Path

PostgreSQL/Supabase can replace the CSV loader later. The first clean migration point is `backend/app/utils/data_loader.py`; endpoint contracts can stay stable while the storage layer changes.

Paid provider adapters should live under `backend/app/ingestion/sources` and produce the same `player_current_profiles.csv` columns before the data is published to the backend.
