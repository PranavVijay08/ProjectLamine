# Project Lamine Backend

FastAPI service for the Player DNA MVP.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

## Endpoints

- `GET /players`
- `GET /players/{player_id}`
- `GET /players/{player_id}/similar`
- `GET /players/{player_id}/compare/{other_player_id}`

Similarity uses `StandardScaler` over numerical player attributes and cosine similarity. The selected player is excluded from recommendation results.

## Active Dataset

The API loads player profiles in this order:

1. `PLAYER_DNA_DATA_PATH` if the environment variable is set
2. `../data/processed/player_current_profiles.csv` if it exists
3. `../data/players_mock.csv` as the local fallback

Build the processed local dataset from the current mock data:

```powershell
python scripts\update_dataset.py --source mock
```

Fetch Top 5 league roster context from football-data.org:

```powershell
$env:FOOTBALL_DATA_ORG_TOKEN="your-token"
python scripts\update_dataset.py --source football-data-org --season 2025
```

Build event-derived profiles from StatsBomb Open Data:

```powershell
python scripts\update_dataset.py --source statsbomb-open --competition-id 11 --season-id 90 --min-minutes 450
```

football-data.org is used for current league/team/player roster context. StatsBomb Open Data is used to develop event-derived metrics, but its free coverage is limited and should not be treated as complete latest Top 5 league coverage.
