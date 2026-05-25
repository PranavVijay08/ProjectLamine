from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from app.ingestion.config import TOP_FIVE_LEAGUES
from app.ingestion.io import (
    PROCESSED_DIR,
    RAW_DIR,
    ensure_data_directories,
    utc_now_iso,
    write_csv,
    write_json,
)
from app.ingestion.sources.base import SourceRunResult
from app.ingestion.sources.football_data_org import FootballDataOrgClient, normalize_rosters
from app.ingestion.sources.statsbomb_open import (
    StatsBombOpenDataClient,
    build_player_profiles_from_events,
)
from app.utils.player_profile_validation import validate_player_profiles


def publish_mock_profiles(mock_csv_path: Path) -> SourceRunResult:
    ensure_data_directories()
    df = validate_player_profiles(pd.read_csv(mock_csv_path))
    output_path = write_csv(PROCESSED_DIR / "player_current_profiles.csv", df)
    metadata_path = write_json(
        PROCESSED_DIR / "player_current_profiles.metadata.json",
        {
            "dataset": "player_current_profiles",
            "source": "local mock data",
            "built_at": utc_now_iso(),
            "row_count": int(len(df)),
            "note": "Mock data is for local development only and should not be presented as real provider data.",
        },
    )
    return SourceRunResult(
        source_name="mock",
        raw_paths=[],
        processed_paths=[output_path, metadata_path],
        notes=["Published mock data to the active processed dataset."],
    )


def fetch_football_data_org_rosters(season: int | None = None) -> SourceRunResult:
    ensure_data_directories()
    client = FootballDataOrgClient(
        api_token=os.getenv("FOOTBALL_DATA_ORG_TOKEN", ""),
        min_requests_available=int(os.getenv("FOOTBALL_DATA_ORG_MIN_REQUESTS_AVAILABLE", "1")),
        throttle_buffer_seconds=int(os.getenv("FOOTBALL_DATA_ORG_THROTTLE_BUFFER_SECONDS", "2")),
    )
    payloads = client.fetch_top_five_league_teams(season=season)
    rate_limit_metadata = client.rate_limit_metadata()

    timestamp = utc_now_iso()
    suffix = str(season) if season else "current"
    raw_path = write_json(RAW_DIR / "football_data_org" / f"top_five_rosters_{suffix}.json", payloads)
    rosters = normalize_rosters(payloads)
    processed_path = write_csv(PROCESSED_DIR / f"top_five_rosters_{suffix}.csv", rosters)
    metadata_path = write_json(
        PROCESSED_DIR / f"top_five_rosters_{suffix}.metadata.json",
        {
            "dataset": f"top_five_rosters_{suffix}",
            "source": "football-data.org",
            "built_at": timestamp,
            "season": season,
            "league_codes": [league.code for league in TOP_FIVE_LEAGUES],
            "row_count": int(len(rosters)),
            "rate_limit": rate_limit_metadata,
            "note": "Roster data is used for current player identity and club context, not advanced Player DNA metrics.",
        },
    )
    last_rate_limit_state = rate_limit_metadata.get("last_rate_limit_state") or {}
    return SourceRunResult(
        source_name="football-data.org",
        raw_paths=[raw_path],
        processed_paths=[processed_path, metadata_path],
        notes=[
            "Fetched Top 5 league roster snapshots.",
            (
                "Last football-data.org rate-limit state: "
                f"{last_rate_limit_state.get('requests_available')} requests available, "
                f"reset in {last_rate_limit_state.get('reset_seconds')} seconds."
            ),
        ],
        metadata={"rate_limit": rate_limit_metadata},
    )


def fetch_statsbomb_open_profiles(
    competition_id: int,
    season_id: int,
    min_minutes: int = 450,
    publish: bool = False,
) -> SourceRunResult:
    ensure_data_directories()
    client = StatsBombOpenDataClient()
    matches = client.fetch_matches(competition_id=competition_id, season_id=season_id)
    events_by_match = {}
    lineups_by_match = {}

    for match in matches:
        match_id = int(match["match_id"])
        events_by_match[match_id] = client.fetch_events(match_id)
        lineups_by_match[match_id] = client.fetch_lineups(match_id)

    suffix = f"competition_{competition_id}_season_{season_id}"
    raw_path = write_json(
        RAW_DIR / "statsbomb_open" / f"{suffix}.json",
        {
            "competition_id": competition_id,
            "season_id": season_id,
            "matches": matches,
            "events_by_match": events_by_match,
            "lineups_by_match": lineups_by_match,
        },
    )
    profiles = build_player_profiles_from_events(
        matches=matches,
        events_by_match=events_by_match,
        lineups_by_match=lineups_by_match,
        min_minutes=min_minutes,
    )

    processed_name = "player_current_profiles.csv" if publish else f"statsbomb_profiles_{suffix}.csv"
    processed_path = write_csv(PROCESSED_DIR / processed_name, profiles)
    metadata_path = write_json(
        PROCESSED_DIR / processed_name.replace(".csv", ".metadata.json"),
        {
            "dataset": processed_name.replace(".csv", ""),
            "source": "StatsBomb Open Data",
            "built_at": utc_now_iso(),
            "competition_id": competition_id,
            "season_id": season_id,
            "min_minutes": min_minutes,
            "row_count": int(len(profiles)),
            "published_as_current": publish,
            "note": (
                "Open-data event profiles are derived locally. Some fields, including xA, age and preferred foot, "
                "are approximated or unavailable unless merged with another provider."
            ),
        },
    )
    return SourceRunResult(
        source_name="statsbomb-open-data",
        raw_paths=[raw_path],
        processed_paths=[processed_path, metadata_path],
        notes=["Built event-derived player profiles from StatsBomb Open Data."],
    )
