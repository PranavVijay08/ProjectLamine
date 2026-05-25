import type { Player } from "./types";

export const numericFeatures = [
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
  "final_third_entries_per90"
] as const;

export const radarFeatures = [
  "goals_per90",
  "assists_per90",
  "key_passes_per90",
  "progressive_passes_per90",
  "progressive_carries_per90",
  "successful_dribbles_per90",
  "pressures_per90",
  "tackles_per90"
] as const;

export const attributeLabels: Record<(typeof numericFeatures)[number], string> = {
  goals_per90: "Goals",
  assists_per90: "Assists",
  xg_per90: "xG",
  xa_per90: "xA",
  shots_per90: "Shots",
  key_passes_per90: "Key passes",
  progressive_passes_per90: "Progressive passes",
  progressive_carries_per90: "Progressive carries",
  successful_dribbles_per90: "Successful dribbles",
  pass_completion_pct: "Pass completion",
  touches_attacking_third_per90: "Attacking-third touches",
  pressures_per90: "Pressures",
  tackles_per90: "Tackles",
  interceptions_per90: "Interceptions",
  aerial_win_pct: "Aerial win rate",
  defensive_duels_won_pct: "Defensive duel win rate",
  carries_into_box_per90: "Carries into box",
  passes_into_box_per90: "Passes into box",
  final_third_entries_per90: "Final-third entries"
};

export const radarCaps: Record<(typeof radarFeatures)[number], number> = {
  goals_per90: 0.9,
  assists_per90: 0.45,
  key_passes_per90: 3.2,
  progressive_passes_per90: 9,
  progressive_carries_per90: 7,
  successful_dribbles_per90: 3.4,
  pressures_per90: 30,
  tackles_per90: 3.8
};

export function metric(player: Player, feature: (typeof numericFeatures)[number]) {
  return Number(player[feature]);
}
