from __future__ import annotations

import argparse
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ingestion.builders import (  # noqa: E402
    fetch_football_data_org_rosters,
    fetch_statsbomb_open_profiles,
    publish_mock_profiles,
)
from app.ingestion.io import REFERENCE_DIR, ensure_data_directories, write_json  # noqa: E402
from app.ingestion.config import TOP_FIVE_LEAGUES  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Build local Player DNA datasets.")
    parser.add_argument(
        "--source",
        choices=["mock", "football-data-org", "statsbomb-open"],
        required=True,
        help="Dataset source to update.",
    )
    parser.add_argument("--season", type=int, default=None, help="Season start year for football-data.org.")
    parser.add_argument("--competition-id", type=int, default=None, help="StatsBomb competition id.")
    parser.add_argument("--season-id", type=int, default=None, help="StatsBomb season id.")
    parser.add_argument("--min-minutes", type=int, default=450, help="Minimum minutes for event-derived profiles.")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish StatsBomb-derived profiles as data/processed/player_current_profiles.csv.",
    )
    args = parser.parse_args()

    ensure_data_directories()
    _write_reference_files()

    if args.source == "mock":
        result = publish_mock_profiles(PROJECT_ROOT / "data" / "players_mock.csv")
    elif args.source == "football-data-org":
        result = fetch_football_data_org_rosters(season=args.season)
    else:
        if args.competition_id is None or args.season_id is None:
            raise SystemExit("--competition-id and --season-id are required for statsbomb-open")
        result = fetch_statsbomb_open_profiles(
            competition_id=args.competition_id,
            season_id=args.season_id,
            min_minutes=args.min_minutes,
            publish=args.publish,
        )

    print(f"Updated {result.source_name}")
    for path in [*result.raw_paths, *result.processed_paths]:
        print(path.relative_to(PROJECT_ROOT))
    for note in result.notes:
        print(note)


def _write_reference_files() -> None:
    write_json(
        REFERENCE_DIR / "league_codes.json",
        {
            "top_five_leagues": [
                {"code": league.code, "name": league.name, "country": league.country}
                for league in TOP_FIVE_LEAGUES
            ]
        },
    )
    write_json(
        REFERENCE_DIR / "source_registry.json",
        {
            "active_sources": {
                "football-data.org": {
                    "use": "Top 5 league rosters, teams, competitions and current club context.",
                    "requires_token": True,
                    "advanced_player_style_metrics": False,
                },
                "StatsBomb Open Data": {
                    "use": "Open event data for developing and testing event-derived Player DNA metrics.",
                    "requires_token": False,
                    "advanced_player_style_metrics": True,
                    "coverage_note": "Selected open competitions only; not full latest Top 5 league coverage.",
                },
            },
            "future_paid_sources": {
                "Wyscout": "Candidate for broad scouting metrics, rosters and event data.",
                "StatsBomb paid API": "Candidate for high-quality event data and advanced modelling.",
                "Opta/Stats Perform": "Candidate for official-grade live and historical football data.",
                "Sportradar": "Candidate for B2B live, seasonal and historical sports data feeds.",
            },
        },
    )


if __name__ == "__main__":
    main()
