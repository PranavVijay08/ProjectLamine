from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import ComparisonResponse, Player, SimilarPlayer
from app.services.similarity_service import SimilarityFilters, SimilarityService
from app.utils.data_loader import load_players


app = FastAPI(title="Project Lamine Player DNA API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_similarity_service() -> SimilarityService:
    return SimilarityService(load_players())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/players", response_model=list[Player])
def players(q: str | None = Query(default=None, description="Search by player, club or league")):
    return get_similarity_service().get_players(query=q)


@app.get("/players/{player_id}", response_model=Player)
def player(player_id: int):
    result = get_similarity_service().get_player(player_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return result


@app.get("/players/{player_id}/similar", response_model=list[SimilarPlayer])
def similar_players(
    player_id: int,
    max_age: int | None = None,
    league: str | None = None,
    position: str | None = None,
    nationality: str | None = None,
):
    try:
        filters = SimilarityFilters(
            max_age=max_age,
            league=league,
            position=position,
            nationality=nationality,
        )
        return get_similarity_service().find_similar(player_id, filters=filters, limit=10)
    except KeyError:
        raise HTTPException(status_code=404, detail="Player not found") from None


@app.get("/players/{player_id}/compare/{other_player_id}", response_model=ComparisonResponse)
def compare_players(player_id: int, other_player_id: int):
    try:
        return get_similarity_service().compare_players(player_id, other_player_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Player not found") from None
