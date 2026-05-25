from functools import lru_cache
import os
from pathlib import Path

import pandas as pd

from app.utils.player_profile_validation import validate_player_profiles

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
MOCK_DATA_PATH = DATA_DIR / "players_mock.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "player_current_profiles.csv"


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
