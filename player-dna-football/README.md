# Project Lamine: Player DNA

Full-stack MVP for a football player similarity app. Users can search a player, inspect a profile, view a radar chart, and find the top 10 most similar players by playing-style attributes.

## Stack

- Frontend: Next.js App Router, TypeScript, Tailwind CSS, Recharts
- Backend: FastAPI, pandas, scikit-learn, numpy
- Data: local CSV mock dataset

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

The backend loads `data/players_mock.csv`, standardises numerical style attributes with `StandardScaler`, calculates cosine similarity, excludes the selected player, applies optional filters, and returns similarity as a percentage.

Optional filters for `/players/{player_id}/similar`:

- `max_age`
- `league`
- `position`
- `nationality`

## Current Limits

- Mock data only
- No authentication
- No paid APIs
- No scraping
- No production database yet
