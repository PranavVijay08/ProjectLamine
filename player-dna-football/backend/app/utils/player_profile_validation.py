from __future__ import annotations

import pandas as pd

from app.player_profile_schema import (
    INTEGER_COLUMNS,
    NUMERIC_FEATURES,
    PERCENTAGE_COLUMNS,
    PLAYER_PROFILE_COLUMNS,
    TEXT_COLUMNS,
)


class PlayerProfileValidationError(ValueError):
    """Raised when a processed Player DNA profile file is not usable by the API."""


def coerce_player_profile_types(df: pd.DataFrame) -> pd.DataFrame:
    coerced = df.copy()

    for column in INTEGER_COLUMNS:
        coerced[column] = pd.to_numeric(coerced[column], errors="raise").astype(int)

    for column in NUMERIC_FEATURES:
        coerced[column] = pd.to_numeric(coerced[column], errors="raise").astype(float)

    for column in TEXT_COLUMNS:
        coerced[column] = coerced[column].astype(str).str.strip()

    return coerced[PLAYER_PROFILE_COLUMNS]


def validate_player_profiles(df: pd.DataFrame, min_minutes: int | None = None) -> pd.DataFrame:
    missing_columns = [column for column in PLAYER_PROFILE_COLUMNS if column not in df.columns]
    if missing_columns:
        joined = ", ".join(missing_columns)
        raise PlayerProfileValidationError(f"Missing required player profile columns: {joined}")

    validated = coerce_player_profile_types(df)

    if validated["player_id"].duplicated().any():
        duplicate_ids = validated.loc[validated["player_id"].duplicated(), "player_id"].tolist()
        raise PlayerProfileValidationError(f"Duplicate player_id values found: {duplicate_ids}")

    if validated[TEXT_COLUMNS].eq("").any().any():
        raise PlayerProfileValidationError("Text fields must not be blank")

    if (validated["minutes"] < 0).any():
        raise PlayerProfileValidationError("minutes must not be negative")

    per90_columns = [column for column in NUMERIC_FEATURES if column.endswith("_per90")]
    if (validated[per90_columns] < 0).any().any():
        raise PlayerProfileValidationError("Per-90 player attributes must not be negative")

    for column in PERCENTAGE_COLUMNS:
        if ((validated[column] < 0) | (validated[column] > 100)).any():
            raise PlayerProfileValidationError(f"{column} must be between 0 and 100")

    if min_minutes is not None:
        validated = validated[validated["minutes"] >= min_minutes].copy()

    return validated.sort_values("player_name").reset_index(drop=True)
