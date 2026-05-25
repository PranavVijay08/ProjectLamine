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
