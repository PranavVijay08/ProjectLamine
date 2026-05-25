from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from app.player_profile_schema import NUMERIC_FEATURES, RADAR_FEATURES
from app.services.explanation_service import build_similarity_explanation, readable_attribute


@dataclass(frozen=True)
class SimilarityFilters:
    max_age: int | None = None
    league: str | None = None
    position: str | None = None
    nationality: str | None = None


class SimilarityService:
    def __init__(self, players: pd.DataFrame):
        self.players = players.copy()
        self.scaler = StandardScaler()
        self.scaled_features = self.scaler.fit_transform(self.players[NUMERIC_FEATURES])

    def get_player(self, player_id: int) -> dict | None:
        match = self.players[self.players["player_id"] == player_id]
        if match.empty:
            return None
        return match.iloc[0].to_dict()

    def get_players(self, query: str | None = None) -> list[dict]:
        df = self.players
        if query:
            search = query.lower()
            df = df[
                df["player_name"].str.lower().str.contains(search)
                | df["club"].str.lower().str.contains(search)
                | df["league"].str.lower().str.contains(search)
            ]
        return df.sort_values("player_name").to_dict(orient="records")

    def find_similar(
        self,
        player_id: int,
        filters: SimilarityFilters | None = None,
        limit: int = 10,
    ) -> list[dict]:
        selected_index = self._index_for_player(player_id)
        selected_row = self.players.iloc[selected_index]

        scores = cosine_similarity(
            self.scaled_features[selected_index].reshape(1, -1),
            self.scaled_features,
        )[0]

        candidates = self.players.copy()
        candidates["similarity_score"] = np.clip(((scores + 1) / 2) * 100, 0, 100)
        candidates = candidates[candidates["player_id"] != player_id]
        candidates = self._apply_filters(candidates, filters)
        candidates = candidates.sort_values("similarity_score", ascending=False).head(limit)

        results = []
        for candidate_index, candidate in candidates.iterrows():
            matching_attributes = self._closest_attributes(selected_index, candidate_index)
            candidate_dict = candidate.drop(labels=["similarity_score"]).to_dict()
            results.append(
                {
                    "player": candidate_dict,
                    "similarity_score": round(float(candidate["similarity_score"]), 1),
                    "matching_attributes": [readable_attribute(attr) for attr in matching_attributes],
                    "explanation": build_similarity_explanation(
                        selected_name=str(selected_row["player_name"]),
                        similar_name=str(candidate["player_name"]),
                        matching_attributes=matching_attributes,
                        selected_style=str(selected_row["style_label"]),
                        similar_style=str(candidate["style_label"]),
                    ),
                }
            )
        return results

    def compare_players(self, player_id: int, other_player_id: int) -> dict:
        selected_index = self._index_for_player(player_id)
        other_index = self._index_for_player(other_player_id)
        player = self.players.iloc[selected_index]
        other = self.players.iloc[other_index]

        score = cosine_similarity(
            self.scaled_features[selected_index].reshape(1, -1),
            self.scaled_features[other_index].reshape(1, -1),
        )[0][0]

        radar_attributes = [
            {
                "attribute": readable_attribute(feature),
                "player": round(float(player[feature]), 2),
                "other_player": round(float(other[feature]), 2),
            }
            for feature in RADAR_FEATURES
        ]
        attribute_deltas = [
            {
                "attribute": readable_attribute(feature),
                "player_value": round(float(player[feature]), 2),
                "other_value": round(float(other[feature]), 2),
                "delta": round(float(player[feature] - other[feature]), 2),
            }
            for feature in NUMERIC_FEATURES
        ]

        return {
            "player": player.to_dict(),
            "other_player": other.to_dict(),
            "similarity_score": round(float(np.clip(((score + 1) / 2) * 100, 0, 100)), 1),
            "radar_attributes": radar_attributes,
            "attribute_deltas": attribute_deltas,
        }

    def _index_for_player(self, player_id: int) -> int:
        matches = self.players.index[self.players["player_id"] == player_id].tolist()
        if not matches:
            raise KeyError(player_id)
        return matches[0]

    def _apply_filters(self, df: pd.DataFrame, filters: SimilarityFilters | None) -> pd.DataFrame:
        if not filters:
            return df
        filtered = df
        if filters.max_age is not None:
            filtered = filtered[filtered["age"] <= filters.max_age]
        if filters.league:
            filtered = self._case_insensitive_equal(filtered, "league", filters.league)
        if filters.position:
            filtered = self._case_insensitive_equal(filtered, "position", filters.position)
        if filters.nationality:
            filtered = self._case_insensitive_equal(filtered, "nationality", filters.nationality)
        return filtered

    @staticmethod
    def _case_insensitive_equal(df: pd.DataFrame, column: str, value: str) -> pd.DataFrame:
        return df[df[column].str.lower() == value.lower()]

    def _closest_attributes(self, selected_index: int, candidate_index: int, limit: int = 3) -> list[str]:
        selected_vector = self.scaled_features[selected_index]
        candidate_vector = self.scaled_features[candidate_index]
        deltas = np.abs(selected_vector - candidate_vector)
        closest_indices: Iterable[int] = np.argsort(deltas)[:limit]
        return [NUMERIC_FEATURES[index] for index in closest_indices]
