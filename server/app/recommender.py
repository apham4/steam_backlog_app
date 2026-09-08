# Recommender engine to gather details and come up with a backlog recommendation.

import urllib.parse
from dataclasses import dataclass
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional, Set

from app import models, steam
from app.config import settings
from app.errors import RecommendationErrorCode

def build_genre_weights(
    recent_with_playtime: List[Dict[str, Any]], 
    recent_game_details: List[models.GamesCache],
) -> Dict[str, float]:
    """From recently played game data, calculate genre -> weight map. TODO: Categories?"""

    playtime_map: Dict[str, int] = {}
    for game in recent_with_playtime:
        playtime_map[game["appid"]] = game.get("playtime_2weeks", 0)

    # genre weights are just the collective playtime of all the recent games containing that genre
    genre_weights: Dict[str, float] = {}
    for game in recent_game_details:
        if not game or not game.genres:
            continue
        playtime = playtime_map.get(game.app_id, 0)
        for genre in game.genres:
            genre_weights[genre] = genre_weights.get(genre, 0.0) + float(playtime)

    # then we normalize to 0.0 -> 1.0 range
    total_weight = sum(genre_weights.values())
    if total_weight > 0:
        for genre in genre_weights:
            genre_weights[genre] /= total_weight

    return genre_weights


@dataclass
class GameScoreData:
    score: float
    matched_genres: List[str]


def score_game(
    game: models.GamesCache,
    genre_weights: Dict[str, float],
) -> Optional[GameScoreData]:
    """Score a backlog game based on genre weights and review scores."""

    if not game:
        return None

    matched_genres = []
    genre_score = 0
    for genre in game.genres:
        if genre in genre_weights:
            genre_score += genre_weights[genre]
            matched_genres.append(genre)

    # Need to normalize review_score (1-9) as well because genre_score is normalized to 0.0-1.0.
    # Divide by 9, then clamp it between 0 and 1.
    review_score = game.review_score or 0
    normalized_review_score = min(max(review_score / 9.0, 0.0), 1.0)
    composite_score = (genre_score * settings.GAME_SCORE_GENRE_WEIGHT) + (normalized_review_score * settings.GAME_SCORE_REVIEW_WEIGHT)

    return GameScoreData(
        score = composite_score,
        matched_genres = matched_genres,
    )


@dataclass
class RecommendationData:
    game_details: models.GamesCache
    store_url: str
    trailer_search_url: str

    recent_games_referenced: List[str]
    matched_genres: List[str]


async def get_top_recommendation(
    current_user: models.User,
    library_details: steam.GameLibraryDetails,
    exclusions: List[models.Exclusion],
    db: Session,
) -> Optional[RecommendationData]:
    """Main function to get a singular backlog game recommendation given the parameters."""

    # User has no games.
    if not library_details or library_details.total_owned == 0:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {"code": RecommendationErrorCode.NO_GAMES.value},
        )

    # User has games but none under the backlog playtime threshold
    if not library_details.backlog or len(library_details.backlog) == 0:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail={
                "code": RecommendationErrorCode.NO_QUALIFYING_BACKLOG.value,
                "params": {"threshold": current_user.settings.backlog_threshold_mins},
            },
        )

    # Filter out exclusions from backlog
    excluded_ids: Set[int] = {exclusion.app_id for exclusion in exclusions} if exclusions else set()
    eligible_backlog = [game for game in library_details.backlog if game["appid"] not in excluded_ids]

    if not eligible_backlog:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = {"code": RecommendationErrorCode.ALL_EXCLUDED.value},
        )

    # Batch fetch recently played games
    recent_app_ids = [game["appid"] for game in library_details.recently_played]
    recent_details: List[models.GamesCache] = await steam.get_games_details_batch(recent_app_ids, db)

    # Use recent game details to weight genres
    genre_weights = build_genre_weights(library_details.recently_played, recent_details)

    # Batch fetch backlog games
    backlog_app_ids = [game["appid"] for game in eligible_backlog]
    backlog_details: List[models.GamesCache] = await steam.get_games_details_batch(backlog_app_ids, db)

    # Score games using the helper
    scored_games = []
    for game in backlog_details:
        score_data: GameScoreData = score_game(game, genre_weights)
        if not score_data:
            continue
        scored_games.append({
            "game": game,
            "score": score_data.score,
            "matched_genres": score_data.matched_genres,
        })

    if not scored_games:
        return None

    # Sort by score
    scored_games.sort(key = lambda x: x["score"], reverse = True)
    best_match = scored_games[0]

    store_url = settings.STEAM_STORE_GAME_URL.format(app_id = best_match["game"].app_id)
    raw_trailer_search_phrase = settings.TRAILER_SEARCH_PHRASE.format(app_name = best_match["game"].name)
    encoded_trailer_search_phrase = urllib.parse.quote_plus(raw_trailer_search_phrase)
    trailer_search_url = settings.TRAILER_SEARCH_URL.format(search_phrase = encoded_trailer_search_phrase)

    return RecommendationData(
        game_details = best_match["game"],
        store_url = store_url,
        trailer_search_url = trailer_search_url,
        recent_games_referenced = [game.name for game in recent_details],
        matched_genres = best_match["matched_genres"],
    )
