# Data Dictionary

The active backend dataset is `data/processed/player_current_profiles.csv` when present, otherwise `data/players_mock.csv`.

| Field | Description |
| --- | --- |
| `player_id` | Stable integer identifier for MVP records |
| `player_name` | Player display name |
| `age` | Player age |
| `nationality` | Player nationality |
| `club` | Current mock club |
| `league` | Current mock league |
| `position` | Primary position |
| `preferred_foot` | Preferred foot |
| `minutes` | Played minutes in the mock sample |
| `goals_per90` | Goals per 90 minutes |
| `assists_per90` | Assists per 90 minutes |
| `xg_per90` | Expected goals per 90 minutes |
| `xa_per90` | Expected assists per 90 minutes |
| `shots_per90` | Shots per 90 minutes |
| `key_passes_per90` | Key passes per 90 minutes |
| `progressive_passes_per90` | Progressive passes per 90 minutes |
| `progressive_carries_per90` | Progressive carries per 90 minutes |
| `successful_dribbles_per90` | Successful dribbles per 90 minutes |
| `pass_completion_pct` | Pass completion percentage |
| `touches_attacking_third_per90` | Attacking-third touches per 90 minutes |
| `pressures_per90` | Pressures per 90 minutes |
| `tackles_per90` | Tackles per 90 minutes |
| `interceptions_per90` | Interceptions per 90 minutes |
| `aerial_win_pct` | Aerial duel win percentage |
| `defensive_duels_won_pct` | Defensive duel win percentage |
| `carries_into_box_per90` | Carries into penalty box per 90 minutes |
| `passes_into_box_per90` | Passes into penalty box per 90 minutes |
| `final_third_entries_per90` | Final-third entries per 90 minutes |
| `style_label` | Human-readable Player DNA archetype |

## Supporting Data Files

| File | Description |
| --- | --- |
| `data/raw/football_data_org/top_five_rosters_*.json` | Raw football-data.org Top 5 league roster snapshots |
| `data/processed/top_five_rosters_*.csv` | Normalised roster context from football-data.org |
| `data/raw/statsbomb_open/*.json` | Raw StatsBomb Open Data match, lineup and event snapshots |
| `data/processed/statsbomb_profiles_*.csv` | Event-derived player profile rows from StatsBomb Open Data |
| `data/reference/league_codes.json` | Top 5 league code mapping |
| `data/reference/source_registry.json` | Current and future data-source purpose notes |

## Source Notes

football-data.org should be treated as roster, team, competition and fixture context for this project. It does not provide the full advanced style profile needed for Player DNA.

StatsBomb Open Data is suitable for developing event-derived football logic, but its free coverage is limited to selected open competitions. Derived fields such as `xa_per90` are local approximations unless replaced by a provider metric.
