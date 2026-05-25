# Data Sources

## Current Source Strategy

Project Lamine does not scrape football statistics websites. The local data layer is designed around API/open-data ingestion, raw snapshots and validated processed outputs.

## football-data.org

Use for:

- Top 5 league codes and competition context
- Current teams
- Current squad/roster context where available
- Fixture, result and standings context later

Do not use as the only Player DNA source. It does not provide the advanced style metrics needed for scout-grade player comparison.

The adapter inspects rate-limit headers on every response and stores the observed values in the generated metadata file:

- `X-RequestsAvailable`
- `X-Requests-Available`
- `X-Requests-Available-Minute`
- `X-RequestCounter-Reset`
- `Retry-After`

When the remaining request budget reaches `FOOTBALL_DATA_ORG_MIN_REQUESTS_AVAILABLE`, the client waits for the reset window plus `FOOTBALL_DATA_ORG_THROTTLE_BUFFER_SECONDS`.

Fetched football-data.org rosters are available through the backend at:

- `GET /data/status`
- `GET /data/football-data-org/rosters`

They are not automatically published to `/players` because `/players` powers the similarity model and requires the full Player DNA metric schema.

## StatsBomb Open Data

Use for:

- Learning and developing event-derived Player DNA metrics
- Testing progression, carrying, passing, pressure and shot-profile logic
- Building example event-derived profiles from selected open competitions

Limitations:

- Free coverage is not complete latest Top 5 league coverage
- Some profile fields are unavailable in open event files and must be approximated or merged from another source
- Derived metrics must be labelled clearly and not presented as official provider xA or proprietary metrics

## Future Paid Sources

The ingestion layer is structured so future adapters can be added under `backend/app/ingestion/sources`.

Best candidates:

- Wyscout for broad scouting coverage and many comparable player metrics
- StatsBomb paid API for high-quality event data
- Opta/Stats Perform for official-grade football feeds
- Sportradar for B2B sports data feeds and live/seasonal coverage

Any future provider should publish into the same `player_current_profiles.csv` schema before the backend uses it.
