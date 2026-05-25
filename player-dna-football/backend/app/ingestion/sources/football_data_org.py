from __future__ import annotations

import json
from datetime import date
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from app.ingestion.config import LeagueConfig, TOP_FIVE_LEAGUES


class FootballDataOrgError(RuntimeError):
    pass


class FootballDataOrgClient:
    base_url = "https://api.football-data.org/v4"

    def __init__(self, api_token: str):
        if not api_token:
            raise FootballDataOrgError("FOOTBALL_DATA_ORG_TOKEN is required")
        self.api_token = api_token

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"

        request = Request(url, headers={"X-Auth-Token": self.api_token})
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise FootballDataOrgError(f"football-data.org request failed: {exc.code} {detail}") from exc

    def fetch_competition_teams(self, league: LeagueConfig, season: int | None = None) -> dict[str, Any]:
        params = {"season": season} if season else None
        return self.get_json(f"/competitions/{league.code}/teams", params=params)

    def fetch_top_five_league_teams(self, season: int | None = None) -> dict[str, Any]:
        return {
            league.code: self.fetch_competition_teams(league, season=season)
            for league in TOP_FIVE_LEAGUES
        }


def normalize_rosters(payloads_by_league: dict[str, dict[str, Any]]) -> pd.DataFrame:
    league_lookup = {league.code: league for league in TOP_FIVE_LEAGUES}
    rows: list[dict[str, Any]] = []

    for league_code, payload in payloads_by_league.items():
        league = league_lookup.get(league_code)
        if league is None:
            continue

        for team in payload.get("teams", []):
            for player in team.get("squad", []):
                position = str(player.get("position") or "Unknown")
                if position.lower() == "goalkeeper":
                    continue

                rows.append(
                    {
                        "source": "football-data.org",
                        "source_player_id": player.get("id"),
                        "player_name": player.get("name"),
                        "age": _age_from_date_of_birth(player.get("dateOfBirth")),
                        "date_of_birth": player.get("dateOfBirth"),
                        "nationality": player.get("nationality") or "Unknown",
                        "club": team.get("name"),
                        "league": league.name,
                        "league_code": league.code,
                        "country": league.country,
                        "position": _compact_position(position),
                        "preferred_foot": "Unknown",
                    }
                )

    return pd.DataFrame(rows).sort_values(["league", "club", "player_name"]).reset_index(drop=True)


def _age_from_date_of_birth(value: str | None) -> int:
    if not value:
        return 0
    born = date.fromisoformat(value)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def _compact_position(position: str) -> str:
    mapping = {
        "Attacker": "FW",
        "Defence": "DF",
        "Defender": "DF",
        "Midfield": "MF",
        "Midfielder": "MF",
        "Offence": "FW",
    }
    return mapping.get(position, position)
