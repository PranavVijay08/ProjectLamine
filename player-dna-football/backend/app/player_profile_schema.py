PLAYER_ID_COLUMNS = [
    "player_id",
    "player_name",
    "age",
    "nationality",
    "club",
    "league",
    "position",
    "preferred_foot",
    "minutes",
]

NUMERIC_FEATURES = [
    "goals_per90",
    "assists_per90",
    "xg_per90",
    "xa_per90",
    "shots_per90",
    "key_passes_per90",
    "progressive_passes_per90",
    "progressive_carries_per90",
    "successful_dribbles_per90",
    "pass_completion_pct",
    "touches_attacking_third_per90",
    "pressures_per90",
    "tackles_per90",
    "interceptions_per90",
    "aerial_win_pct",
    "defensive_duels_won_pct",
    "carries_into_box_per90",
    "passes_into_box_per90",
    "final_third_entries_per90",
]

RADAR_FEATURES = [
    "goals_per90",
    "assists_per90",
    "key_passes_per90",
    "progressive_passes_per90",
    "progressive_carries_per90",
    "successful_dribbles_per90",
    "pressures_per90",
    "tackles_per90",
]

PLAYER_PROFILE_COLUMNS = [
    *PLAYER_ID_COLUMNS,
    *NUMERIC_FEATURES,
    "style_label",
]

INTEGER_COLUMNS = ["player_id", "age", "minutes"]

TEXT_COLUMNS = [
    "player_name",
    "nationality",
    "club",
    "league",
    "position",
    "preferred_foot",
    "style_label",
]

PERCENTAGE_COLUMNS = [
    "pass_completion_pct",
    "aerial_win_pct",
    "defensive_duels_won_pct",
]
