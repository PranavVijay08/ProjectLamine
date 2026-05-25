from typing import Any

from pydantic import BaseModel


class Player(BaseModel):
    player_id: int
    player_name: str
    age: int
    nationality: str
    club: str
    league: str
    position: str
    preferred_foot: str
    minutes: int
    goals_per90: float
    assists_per90: float
    xg_per90: float
    xa_per90: float
    shots_per90: float
    key_passes_per90: float
    progressive_passes_per90: float
    progressive_carries_per90: float
    successful_dribbles_per90: float
    pass_completion_pct: float
    touches_attacking_third_per90: float
    pressures_per90: float
    tackles_per90: float
    interceptions_per90: float
    aerial_win_pct: float
    defensive_duels_won_pct: float
    carries_into_box_per90: float
    passes_into_box_per90: float
    final_third_entries_per90: float
    style_label: str


class SimilarPlayer(BaseModel):
    player: Player
    similarity_score: float
    explanation: str
    matching_attributes: list[str]


class ComparisonResponse(BaseModel):
    player: Player
    other_player: Player
    similarity_score: float
    radar_attributes: list[dict[str, Any]]
    attribute_deltas: list[dict[str, Any]]
