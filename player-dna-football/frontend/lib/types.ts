export type Player = {
  player_id: number;
  player_name: string;
  age: number;
  nationality: string;
  club: string;
  league: string;
  position: string;
  preferred_foot: string;
  minutes: number;
  goals_per90: number;
  assists_per90: number;
  xg_per90: number;
  xa_per90: number;
  shots_per90: number;
  key_passes_per90: number;
  progressive_passes_per90: number;
  progressive_carries_per90: number;
  successful_dribbles_per90: number;
  pass_completion_pct: number;
  touches_attacking_third_per90: number;
  pressures_per90: number;
  tackles_per90: number;
  interceptions_per90: number;
  aerial_win_pct: number;
  defensive_duels_won_pct: number;
  carries_into_box_per90: number;
  passes_into_box_per90: number;
  final_third_entries_per90: number;
  style_label: string;
};

export type SimilarPlayer = {
  player: Player;
  similarity_score: number;
  explanation: string;
  matching_attributes: string[];
};

export type ComparisonResponse = {
  player: Player;
  other_player: Player;
  similarity_score: number;
  radar_attributes: Array<{
    attribute: string;
    player: number;
    other_player: number;
  }>;
  attribute_deltas: Array<{
    attribute: string;
    player_value: number;
    other_value: number;
    delta: number;
  }>;
};

export type SimilarFilters = {
  max_age?: string;
  league?: string;
  position?: string;
  nationality?: string;
};
