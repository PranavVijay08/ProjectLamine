from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LeagueConfig:
    code: str
    name: str
    country: str


TOP_FIVE_LEAGUES = [
    LeagueConfig(code="PL", name="Premier League", country="England"),
    LeagueConfig(code="PD", name="La Liga", country="Spain"),
    LeagueConfig(code="FL1", name="Ligue 1", country="France"),
    LeagueConfig(code="SA", name="Serie A", country="Italy"),
    LeagueConfig(code="BL1", name="Bundesliga", country="Germany"),
]

STATSBOMB_OPEN_DATA_BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
