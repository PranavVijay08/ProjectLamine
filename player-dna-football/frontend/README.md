# Project Lamine Frontend

Next.js App Router frontend for the Player DNA MVP.

## Setup

```bash
npm install
npm run dev
```

The app runs at `http://localhost:3000`.

## API

By default the frontend calls `http://localhost:8000`. Override with:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

If the API is unavailable, the frontend reads `public/players_mock.csv` and computes similarity locally for MVP development.
