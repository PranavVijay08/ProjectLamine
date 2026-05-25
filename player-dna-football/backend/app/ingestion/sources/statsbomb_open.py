from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen

import pandas as pd

from app.ingestion.config import STATSBOMB_OPEN_DATA_BASE_URL
from app.player_profile_schema import PLAYER_PROFILE_COLUMNS
from app.utils.player_profile_validation import validate_player_profiles


class StatsBombOpenDataError(RuntimeError):
    pass


class StatsBombOpenDataClient:
    def __init__(self, base_url: str = STATSBOMB_OPEN_DATA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def fetch_json(self, path: str) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            with urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise StatsBombOpenDataError(f"StatsBomb Open Data request failed: {exc.code} {detail}") from exc

    def fetch_competitions(self) -> list[dict[str, Any]]:
        return self.fetch_json("competitions.json")

    def fetch_matches(self, competition_id: int, season_id: int) -> list[dict[str, Any]]:
        return self.fetch_json(f"matches/{competition_id}/{season_id}.json")

    def fetch_events(self, match_id: int) -> list[dict[str, Any]]:
        return self.fetch_json(f"events/{match_id}.json")

    def fetch_lineups(self, match_id: int) -> list[dict[str, Any]]:
        return self.fetch_json(f"lineups/{match_id}.json")


def build_player_profiles_from_events(
    matches: list[dict[str, Any]],
    events_by_match: dict[int, list[dict[str, Any]]],
    lineups_by_match: dict[int, list[dict[str, Any]]],
    min_minutes: int = 450,
) -> pd.DataFrame:
    aggregates: dict[int, dict[str, Any]] = defaultdict(_new_player_aggregate)
    minutes_by_player = _estimate_minutes_by_player(lineups_by_match)
    position_votes: dict[int, Counter[str]] = defaultdict(Counter)

    match_lookup = {int(match["match_id"]): match for match in matches}
    for match_id, events in events_by_match.items():
        match = match_lookup.get(match_id, {})
        league_name = str(match.get("competition", {}).get("competition_name") or "StatsBomb Open Data")

        for event in events:
            player = event.get("player")
            if not player:
                continue

            player_id = int(player["id"])
            row = aggregates[player_id]
            row["player_id"] = player_id
            row["player_name"] = player["name"]
            row["club"] = event.get("team", {}).get("name") or "Unknown"
            row["league"] = league_name
            row["minutes"] = max(row["minutes"], int(minutes_by_player.get(player_id, 0)))

            position_name = event.get("position", {}).get("name")
            if position_name:
                position_votes[player_id][_compact_position(position_name)] += 1

            _add_event_to_aggregate(row, event)

    rows = []
    for player_id, row in aggregates.items():
        row["position"] = _most_common_position(position_votes[player_id])
        if row["position"] == "GK":
            continue
        rows.append(_finalize_profile_row(row))

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=PLAYER_PROFILE_COLUMNS)
    return validate_player_profiles(df, min_minutes=min_minutes)


def _new_player_aggregate() -> dict[str, Any]:
    return {
        "player_id": 0,
        "player_name": "",
        "age": 0,
        "nationality": "Unknown",
        "club": "Unknown",
        "league": "StatsBomb Open Data",
        "position": "Unknown",
        "preferred_foot": "Unknown",
        "minutes": 0,
        "goals": 0,
        "assists": 0,
        "xg": 0.0,
        "shots": 0,
        "key_passes": 0,
        "passes": 0,
        "completed_passes": 0,
        "progressive_passes": 0,
        "progressive_carries": 0,
        "successful_dribbles": 0,
        "attacking_third_touches": 0,
        "pressures": 0,
        "tackles": 0,
        "interceptions": 0,
        "aerial_duels": 0,
        "aerial_duels_won": 0,
        "defensive_duels": 0,
        "defensive_duels_won": 0,
        "carries_into_box": 0,
        "passes_into_box": 0,
        "final_third_entries": 0,
    }


def _add_event_to_aggregate(row: dict[str, Any], event: dict[str, Any]) -> None:
    event_type = event.get("type", {}).get("name")
    location = event.get("location") or []
    start_x = float(location[0]) if len(location) >= 1 else None

    if start_x is not None and start_x >= 80:
        row["attacking_third_touches"] += 1

    if event_type == "Shot":
        row["shots"] += 1
        row["xg"] += float(event.get("shot", {}).get("statsbomb_xg") or 0)
        if event.get("shot", {}).get("outcome", {}).get("name") == "Goal":
            row["goals"] += 1
        return

    if event_type == "Pass":
        pass_data = event.get("pass", {})
        end_location = pass_data.get("end_location") or []
        end_x = float(end_location[0]) if len(end_location) >= 1 else None
        row["passes"] += 1
        if "outcome" not in pass_data:
            row["completed_passes"] += 1
        if pass_data.get("goal_assist"):
            row["assists"] += 1
        if pass_data.get("shot_assist") or pass_data.get("goal_assist"):
            row["key_passes"] += 1
        if _is_progressive(start_x, end_x):
            row["progressive_passes"] += 1
        if _is_box_entry(end_location):
            row["passes_into_box"] += 1
        if _is_final_third_entry(start_x, end_x):
            row["final_third_entries"] += 1
        return

    if event_type == "Carry":
        carry_data = event.get("carry", {})
        end_location = carry_data.get("end_location") or []
        end_x = float(end_location[0]) if len(end_location) >= 1 else None
        if _is_progressive(start_x, end_x):
            row["progressive_carries"] += 1
        if _is_box_entry(end_location):
            row["carries_into_box"] += 1
        if _is_final_third_entry(start_x, end_x):
            row["final_third_entries"] += 1
        return

    if event_type == "Dribble":
        if event.get("dribble", {}).get("outcome", {}).get("name") == "Complete":
            row["successful_dribbles"] += 1
        return

    if event_type == "Pressure":
        row["pressures"] += 1
        return

    if event_type == "Interception":
        row["interceptions"] += 1
        return

    if event_type == "Duel":
        duel_data = event.get("duel", {})
        duel_type = duel_data.get("type", {}).get("name", "")
        outcome = duel_data.get("outcome", {}).get("name", "")
        if "Tackle" in duel_type:
            row["tackles"] += 1
        if "Aerial" in duel_type:
            row["aerial_duels"] += 1
            if "Won" in outcome:
                row["aerial_duels_won"] += 1
        else:
            row["defensive_duels"] += 1
            if "Won" in outcome or "Success" in outcome:
                row["defensive_duels_won"] += 1


def _finalize_profile_row(row: dict[str, Any]) -> dict[str, Any]:
    minutes = max(int(row["minutes"]), 1)
    per90 = 90 / minutes
    pass_completion = (row["completed_passes"] / row["passes"] * 100) if row["passes"] else 0
    aerial_win_pct = (row["aerial_duels_won"] / row["aerial_duels"] * 100) if row["aerial_duels"] else 0
    defensive_win_pct = (
        row["defensive_duels_won"] / row["defensive_duels"] * 100
        if row["defensive_duels"]
        else 0
    )

    profile = {
        "player_id": int(row["player_id"]),
        "player_name": row["player_name"],
        "age": int(row["age"]),
        "nationality": row["nationality"],
        "club": row["club"],
        "league": row["league"],
        "position": row["position"],
        "preferred_foot": row["preferred_foot"],
        "minutes": minutes,
        "goals_per90": round(row["goals"] * per90, 2),
        "assists_per90": round(row["assists"] * per90, 2),
        "xg_per90": round(row["xg"] * per90, 2),
        "xa_per90": round(row["key_passes"] * 0.08 * per90, 2),
        "shots_per90": round(row["shots"] * per90, 2),
        "key_passes_per90": round(row["key_passes"] * per90, 2),
        "progressive_passes_per90": round(row["progressive_passes"] * per90, 2),
        "progressive_carries_per90": round(row["progressive_carries"] * per90, 2),
        "successful_dribbles_per90": round(row["successful_dribbles"] * per90, 2),
        "pass_completion_pct": round(pass_completion, 1),
        "touches_attacking_third_per90": round(row["attacking_third_touches"] * per90, 2),
        "pressures_per90": round(row["pressures"] * per90, 2),
        "tackles_per90": round(row["tackles"] * per90, 2),
        "interceptions_per90": round(row["interceptions"] * per90, 2),
        "aerial_win_pct": round(aerial_win_pct, 1),
        "defensive_duels_won_pct": round(defensive_win_pct, 1),
        "carries_into_box_per90": round(row["carries_into_box"] * per90, 2),
        "passes_into_box_per90": round(row["passes_into_box"] * per90, 2),
        "final_third_entries_per90": round(row["final_third_entries"] * per90, 2),
    }
    profile["style_label"] = _style_label(profile)
    return profile


def _estimate_minutes_by_player(lineups_by_match: dict[int, list[dict[str, Any]]]) -> dict[int, float]:
    minutes_by_player: dict[int, float] = defaultdict(float)

    for lineups in lineups_by_match.values():
        for team in lineups:
            for player in team.get("lineup", []):
                player_id = int(player["player_id"])
                minutes = 0.0
                for position in player.get("positions", []):
                    start = _minute_from_time(position.get("from"))
                    end = _minute_from_time(position.get("to")) or 90.0
                    minutes += max(end - start, 0)
                minutes_by_player[player_id] += minutes

    return minutes_by_player


def _minute_from_time(value: str | None) -> float:
    if not value:
        return 0.0
    minute_text, _, second_text = value.partition(":")
    return float(minute_text or 0) + (float(second_text or 0) / 60)


def _is_progressive(start_x: float | None, end_x: float | None) -> bool:
    return start_x is not None and end_x is not None and end_x - start_x >= 10


def _is_final_third_entry(start_x: float | None, end_x: float | None) -> bool:
    return start_x is not None and end_x is not None and start_x < 80 <= end_x


def _is_box_entry(location: list[Any]) -> bool:
    if len(location) < 2:
        return False
    x, y = float(location[0]), float(location[1])
    return x >= 102 and 18 <= y <= 62


def _compact_position(position: str) -> str:
    position = position.lower()
    if "goalkeeper" in position:
        return "GK"
    if "center back" in position or "centre back" in position:
        return "CB"
    if "center forward" in position or "striker" in position:
        return "ST"
    if "wing" in position:
        return "W"
    if "attacking midfield" in position:
        return "AM"
    if "midfield" in position:
        return "CM"
    if "back" in position:
        return "FB"
    return "Unknown"


def _most_common_position(votes: Counter[str]) -> str:
    if not votes:
        return "Unknown"
    return votes.most_common(1)[0][0]


def _style_label(profile: dict[str, Any]) -> str:
    if profile["progressive_carries_per90"] >= 3 and profile["successful_dribbles_per90"] >= 1.5:
        return "Direct ball-carrying winger"
    if profile["key_passes_per90"] >= 2 and profile["progressive_passes_per90"] >= 4:
        return "High-volume chance creator"
    if profile["tackles_per90"] >= 2 or profile["pressures_per90"] >= 18:
        return "Defensive ball-winner"
    if profile["progressive_passes_per90"] >= 5 and profile["pass_completion_pct"] >= 85:
        return "Deep-lying distributor"
    return "Balanced role player"
