from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import time
from datetime import date
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from app.ingestion.config import LeagueConfig, TOP_FIVE_LEAGUES


class FootballDataOrgError(RuntimeError):
    pass


@dataclass(frozen=True)
class FootballDataOrgRateLimitState:
    requests_available: int | None
    reset_seconds: int | None
    retry_after_seconds: int | None
    api_version: str | None
    authenticated_client: str | None
    url_path: str


class FootballDataOrgClient:
    base_url = "https://api.football-data.org/v4"
    remaining_header_names = [
        "X-RequestsAvailable",
        "X-Requests-Available",
        "X-Requests-Available-Minute",
    ]

    def __init__(
        self,
        api_token: str,
        min_requests_available: int = 1,
        throttle_buffer_seconds: int = 2,
        max_retries: int = 3,
    ):
        if not api_token:
            raise FootballDataOrgError("FOOTBALL_DATA_ORG_TOKEN is required")
        self.api_token = api_token
        self.min_requests_available = min_requests_available
        self.throttle_buffer_seconds = throttle_buffer_seconds
        self.max_retries = max_retries
        self.last_rate_limit_state: FootballDataOrgRateLimitState | None = None
        self.rate_limit_history: list[FootballDataOrgRateLimitState] = []
        self.sleep_history: list[dict[str, Any]] = []

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        if params:
            url = f"{url}?{urlencode(params)}"

        request = Request(url, headers={"X-Auth-Token": self.api_token})
        for attempt in range(self.max_retries + 1):
            self._throttle_before_request(path)
            try:
                with urlopen(request, timeout=30) as response:
                    self._record_rate_limit_headers(response.headers, path)
                    return json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                self._record_rate_limit_headers(exc.headers, path)
                if exc.code == 429 and attempt < self.max_retries:
                    self._sleep_for_rate_limit(path, forced=True)
                    continue
                detail = exc.read().decode("utf-8", errors="replace")
                raise FootballDataOrgError(
                    f"football-data.org request failed: {exc.code} {detail}"
                ) from exc

        raise FootballDataOrgError("football-data.org request failed after retries")

    def fetch_competition_teams(self, league: LeagueConfig, season: int | None = None) -> dict[str, Any]:
        params = {"season": season} if season else None
        return self.get_json(f"/competitions/{league.code}/teams", params=params)

    def fetch_top_five_league_teams(self, season: int | None = None) -> dict[str, Any]:
        return {
            league.code: self.fetch_competition_teams(league, season=season)
            for league in TOP_FIVE_LEAGUES
        }

    def rate_limit_metadata(self) -> dict[str, Any]:
        return {
            "min_requests_available": self.min_requests_available,
            "throttle_buffer_seconds": self.throttle_buffer_seconds,
            "last_rate_limit_state": (
                asdict(self.last_rate_limit_state) if self.last_rate_limit_state else None
            ),
            "rate_limit_history": [asdict(item) for item in self.rate_limit_history],
            "sleep_history": self.sleep_history,
        }

    def _throttle_before_request(self, path: str) -> None:
        state = self.last_rate_limit_state
        if state is None or state.requests_available is None:
            return
        if state.requests_available > self.min_requests_available:
            return
        self._sleep_for_rate_limit(path, forced=False)

    def _sleep_for_rate_limit(self, path: str, forced: bool) -> None:
        state = self.last_rate_limit_state
        reset_seconds = state.reset_seconds if state else None
        retry_after_seconds = state.retry_after_seconds if state else None
        wait_seconds = retry_after_seconds or reset_seconds or 60
        wait_seconds = max(wait_seconds + self.throttle_buffer_seconds, 1)
        self.sleep_history.append(
            {
                "path": path,
                "seconds": wait_seconds,
                "reason": "429 retry" if forced else "low remaining request budget",
            }
        )
        time.sleep(wait_seconds)

    def _record_rate_limit_headers(self, headers: Any, path: str) -> None:
        state = FootballDataOrgRateLimitState(
            requests_available=self._first_int_header(headers, self.remaining_header_names),
            reset_seconds=self._int_header(headers, "X-RequestCounter-Reset"),
            retry_after_seconds=self._int_header(headers, "Retry-After"),
            api_version=self._str_header(headers, "X-API-Version"),
            authenticated_client=self._str_header(headers, "X-Authenticated-Client"),
            url_path=path,
        )
        self.last_rate_limit_state = state
        self.rate_limit_history.append(state)

    @staticmethod
    def _str_header(headers: Any, name: str) -> str | None:
        value = headers.get(name) if headers else None
        return str(value) if value is not None else None

    @classmethod
    def _int_header(cls, headers: Any, name: str) -> int | None:
        value = cls._str_header(headers, name)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            return None

    @classmethod
    def _first_int_header(cls, headers: Any, names: list[str]) -> int | None:
        for name in names:
            value = cls._int_header(headers, name)
            if value is not None:
                return value
        return None


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
