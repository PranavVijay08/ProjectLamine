# Project Lamine: Player DNA

Full-stack MVP for a football player similarity app. Users can search a player, inspect a profile, view a radar chart, and find the top 10 most similar players by playing-style attributes.

## Stack

- Frontend: Next.js App Router, TypeScript, Tailwind CSS, Recharts
- Backend: FastAPI, pandas, scikit-learn, numpy
- Data: local CSV mock dataset plus a scalable raw/processed ingestion pipeline

## Project Structure

```text
player-dna-football/
  frontend/
  backend/
  data/
  notebooks/
  docs/
```

## Backend Setup

```bash
cd player-dna-football/backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

## Frontend Setup

```bash
cd player-dna-football/frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`.

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` if you want to override the default API URL.

## MVP Flow

1. Open `/` for the dashboard homepage.
2. Open `/players` and search by player, club or league.
3. Open `/players/[id]` to view a player profile and radar chart.
4. Open `/players/[id]/similar` to see top 10 similar players, explanations and comparison table.

The frontend tries the FastAPI backend first. If the backend is not running, it falls back to `frontend/public/players_mock.csv` and computes MVP similarity locally.

## Similarity Method

The backend prefers `data/processed/player_current_profiles.csv` when it exists. If that file has not been built yet, it falls back to `data/players_mock.csv`.

It standardises numerical style attributes with `StandardScaler`, calculates cosine similarity, excludes the selected player, applies optional filters, and returns similarity as a percentage.

Optional filters for `/players/{player_id}/similar`:

- `max_age`
- `league`
- `position`
- `nationality`

## Current Limits

- Top 5 league roster ingestion is supported through football-data.org
- Event-derived profile building is supported through StatsBomb Open Data for selected open competitions
- The active local dataset still defaults to mock data until a processed profile file is published
- No authentication
- No paid APIs
- No scraping
- No production database yet

## Dataset Updates

From PowerShell:

```powershell
cd player-dna-football\backend
python scripts\update_dataset.py --source mock
```

To fetch Top 5 league roster snapshots from football-data.org:

```powershell
$env:FOOTBALL_DATA_ORG_TOKEN="your-token"
python scripts\update_dataset.py --source football-data-org --season 2025
```

To build event-derived profiles from a StatsBomb Open Data competition:

```powershell
python scripts\update_dataset.py --source statsbomb-open --competition-id 11 --season-id 90 --min-minutes 450
```

Use `--publish` only when you intentionally want the StatsBomb-derived file to become the active backend dataset.
