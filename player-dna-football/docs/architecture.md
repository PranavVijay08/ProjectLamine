# Architecture

## Overview

Project Lamine is split into a Next.js frontend and a FastAPI backend. The MVP uses a local CSV dataset so the product can be tested before connecting to a production data source.

## Backend

FastAPI exposes four core endpoints:

- `GET /players`
- `GET /players/{player_id}`
- `GET /players/{player_id}/similar`
- `GET /players/{player_id}/compare/{other_player_id}`

The backend loads `data/players_mock.csv` through `app/utils/data_loader.py`. Similarity logic lives in `app/services/similarity_service.py`, while explanation text lives in `app/services/explanation_service.py`.

## Similarity Pipeline

1. Load player rows from CSV.
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
