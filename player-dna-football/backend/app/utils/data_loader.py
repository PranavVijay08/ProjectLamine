from functools import lru_cache
from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[3] / "data" / "players_mock.csv"


@lru_cache(maxsize=1)
def load_players() -> pd.DataFrame:
    """Load the local MVP player CSV once per process."""
    df = pd.read_csv(DATA_PATH)
    df["player_id"] = df["player_id"].astype(int)
    df["age"] = df["age"].astype(int)
    df["minutes"] = df["minutes"].astype(int)
    return df
