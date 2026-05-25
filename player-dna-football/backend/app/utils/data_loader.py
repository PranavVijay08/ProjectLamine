from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

from app.utils.player_profile_validation import validate_player_profiles

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
MOCK_DATA_PATH = DATA_DIR / "players_mock.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "player_current_profiles.csv"
PROCESSED_DIR = DATA_DIR / "processed"


def resolve_player_data_path() -> Path:
    override_path = os.getenv("PLAYER_DNA_DATA_PATH")
    if override_path:
        return Path(override_path).expanduser().resolve()
    if PROCESSED_DATA_PATH.exists():
        return PROCESSED_DATA_PATH
    return MOCK_DATA_PATH


@lru_cache(maxsize=1)
def load_players() -> pd.DataFrame:
    """Load and validate the active Player DNA dataset once per process."""
    data_path = resolve_player_data_path()
    df = pd.read_csv(data_path)
    return validate_player_profiles(df)


def active_dataset_status() -> dict[str, Any]:
    data_path = resolve_player_data_path()
    metadata_path = data_path.with_suffix(".metadata.json")
    df = load_players()
    return {
        "active_player_profile_path": str(data_path),
        "active_player_profile_rows": int(len(df)),
        "active_player_profile_source": _metadata_source(metadata_path),
        "active_player_profile_metadata": _read_json(metadata_path),
        "latest_football_data_org_roster": latest_football_data_org_roster_status(),
    }


def latest_football_data_org_roster_path() -> Path | None:
    roster_paths = sorted(PROCESSED_DIR.glob("top_five_rosters_*.csv"), key=lambda path: path.stat().st_mtime)
    return roster_paths[-1] if roster_paths else None


def latest_football_data_org_roster_status() -> dict[str, Any] | None:
    roster_path = latest_football_data_org_roster_path()
    if roster_path is None:
        return None

    df = pd.read_csv(roster_path)
    metadata_path = roster_path.with_suffix(".metadata.json")
    return {
        "path": str(roster_path),
        "rows": int(len(df)),
        "metadata": _read_json(metadata_path),
    }


def load_latest_football_data_org_rosters(
    query: str | None = None,
    league: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    roster_path = latest_football_data_org_roster_path()
    if roster_path is None:
        return []

    df = pd.read_csv(roster_path)
    if league:
        df = df[df["league"].str.lower() == league.lower()]
    if query:
        search = query.lower()
        df = df[
            df["player_name"].str.lower().str.contains(search, na=False)
            | df["club"].str.lower().str.contains(search, na=False)
            | df["league"].str.lower().str.contains(search, na=False)
        ]
    return df.sort_values(["league", "club", "player_name"]).head(limit).to_dict(orient="records")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _metadata_source(path: Path) -> str:
    metadata = _read_json(path) or {}
    return str(metadata.get("source") or "unknown")
