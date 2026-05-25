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

## Environment Variables

Create `backend/.env` for local secrets. This file is ignored by git and should not be committed.

```env
FOOTBALL_DATA_ORG_TOKEN=your-api-key
FOOTBALL_DATA_ORG_MIN_REQUESTS_AVAILABLE=1
FOOTBALL_DATA_ORG_THROTTLE_BUFFER_SECONDS=2
PLAYER_DNA_DATA_PATH=
```

`scripts/update_dataset.py` and the FastAPI app load `backend/.env` automatically. Existing terminal environment variables still win, so you can override a value temporarily from PowerShell when needed.

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
python scripts\update_dataset.py --source football-data-org --season 2025
```

The football-data.org adapter reads the provider's rate-limit response headers after each request:

- `X-RequestsAvailable`
- `X-Requests-Available`
- `X-Requests-Available-Minute`
- `X-RequestCounter-Reset`
- `Retry-After` on `429` responses

It waits automatically when the remaining request budget is at or below the configured threshold. You can tune this from PowerShell:

```powershell
$env:FOOTBALL_DATA_ORG_MIN_REQUESTS_AVAILABLE="2"
$env:FOOTBALL_DATA_ORG_THROTTLE_BUFFER_SECONDS="3"
python scripts\update_dataset.py --source football-data-org --season 2025
```

Or per run:

```powershell
python scripts\update_dataset.py --source football-data-org --season 2025 --min-requests-available 2 --throttle-buffer-seconds 3
```

Build event-derived profiles from StatsBomb Open Data:

```powershell
python scripts\update_dataset.py --source statsbomb-open --competition-id 11 --season-id 90 --min-minutes 450
```

football-data.org is used for current league/team/player roster context. StatsBomb Open Data is used to develop event-derived metrics, but its free coverage is limited and should not be treated as complete latest Top 5 league coverage.
