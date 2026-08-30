# Communications with Steam Web API.

import asyncio
import html
import httpx
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from app import models
from app.config import settings

# region Library Owned Games
async def fetch_owned_games(steam_id: str) -> List[Dict[str, Any]]:
    """Fetch the list of owned games for a given Steam ID using the Steam Web API."""
    url = settings.STEAM_GET_OWNED_GAMES_URL
    params = {
        "key": settings.STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_played_free_games": 1,
        "format": "json",
    }

    # Set up HTTP client, the body is run asynchronously. On exit it closes connections, SSL sessions, free up resources, etc.
    # Equivalent:
    # try:
    #   response = await client.get(...)
    # finally:
    #   await client.aclose()
    async with httpx.AsyncClient(timeout = settings.STEAM_API_TIMEOUT_SECONDS) as client:
        response = await client.get(url, params = params)
        response.raise_for_status() # If error (400 or 500), this raises an httpx.HTTPStatusError exception and stop executing the block.
        return response.json().get("response", {}).get("games", [])


@dataclass
class GameLibraryDetails:
    total_owned: int
    backlog: List[Dict[str, Any]]
    recently_played: List[Dict[str, Any]]

# Haven't figured out what's a good way to specify the output type of this function yet.
async def get_game_library_details(current_user: models.User) -> Optional[GameLibraryDetails]:
    """Get user's library details and specify out backlog and recently played games."""
    library = await fetch_owned_games(current_user.steam_id)
    if not library:
        return None

    backlog_threshold = current_user.settings.backlog_threshold_mins
    recent_threshold = current_user.settings.recent_threshold_mins
    
    backlog_list = []
    recently_played_list = []
    
    for game in library:
        if game.get("playtime_2weeks", 0) >= recent_threshold:
            recently_played_list.append(game)
            continue # If a game is already added as recently played, don't mark it as backlog.
        if game.get("playtime_forever", float('inf')) <= backlog_threshold:
            backlog_list.append(game)

    return GameLibraryDetails(
        total_owned = len(library),
        backlog = backlog_list,
        recently_played = recently_played_list,
    )

# endregion

# region Game Details
async def fetch_game_details_from_steam(in_app_id: int) -> Optional[Dict[str, Any]]:
    """Fetch detailed information for a specific game using the Steam Web API."""
    game_details_url = settings.STEAM_FETCH_APP_DETAILS_URL
    game_reviews_url = settings.STEAM_FETCH_APP_REVIEWS_URL.format(app_id = in_app_id)

    game_details_params = {
        "appids": in_app_id,
    }
    game_reviews_params = {
        "json": 1,
        "purchase_type": "all",
        "num_per_page": 0,
    }

    async with httpx.AsyncClient(timeout = settings.STEAM_API_TIMEOUT_SECONDS) as client:
        # Use asyncio to execute them concurrently, cutting down on response time.
        details_response, reviews_response = await asyncio.gather(
            client.get(game_details_url, params = game_details_params),
            client.get(game_reviews_url, params = game_reviews_params),
            return_exceptions = True # All tasks run regardless of failure. If failed, the return value will be Exception instead of httpx.Response
        )

        # We are not doing raise_for_status() here because it would be bad to crash a whole batch job because of 1 failed game fetch, and Steam API runs into 429 a lot for game details (rate limit).

        # Process details_response
        if isinstance(details_response, Exception) or details_response.status_code != 200:
            # If it is an Exception (because of asyncio) or status code is not success
            return None

        response_result = details_response.json().get(str(in_app_id), {})
        game_data = response_result.get("data", {})
        if not response_result.get("success", False) or game_data.get("type") != "game":
            # If success = False in response or if this app is not a game
            return None

        categories = []
        for category_data in game_data.get("categories", []):
            if "description" in category_data:
                categories.append(category_data["description"])

        genres = []
        for genre_data in game_data.get("genres", []):
            if "description" in genre_data:
                genres.append(genre_data["description"])

        # Process reviews_data
        reviews_data = (
            reviews_response.json().get("query_summary", {})
            if not isinstance(reviews_response, Exception) and reviews_response.status_code == 200
            else {}
        )

        return {
            "app_id": in_app_id,
            "name": html.unescape(game_data.get("name", "MISSING NAME")),
            "image_url": game_data.get("header_image", ""),
            "review_score": reviews_data.get("review_score", 0),
            "total_reviews": reviews_data.get("total_reviews", 0),
            "review_score_desc": reviews_data.get("review_score_desc", ""),
            "developers": game_data.get("developers", []),
            "publishers":game_data.get("publishers", []),
            "short_description": html.unescape(game_data.get("short_description", "")), # Long text can have escape characters.
            "categories": categories,
            "genres": genres,
        }


async def get_games_details_batch(
    app_ids: List[int],
    db: Session,
) -> List[models.GamesCache]:
    """
    First, a single database query to get all cache-hit games.
    Then, among the cache misses/stale, it randomly samples up to the fetch max limit (defined in settings) to fetch from Steam.
    After that, save the new game details to cache with 1 database query.
    """

    if len(app_ids) == 0:
        return []

    # If a game cache was made before this cutoff, it is stale
    freshness_cutoff = datetime.now(timezone.utc) - timedelta(days = settings.GAME_CACHE_TTL_DAYS)

    existing_records = db.query(models.GamesCache).filter(models.GamesCache.app_id.in_(app_ids)).all()
    records_by_id = {record.app_id: record for record in existing_records} # Make it an id -> cache record map

    # Identify cache hits and misses
    cache_hits: List[models.GamesCache] = []
    cache_misses_ids: List[int] = []

    for id in app_ids:
        record = records_by_id.get(id)
        if record and record.last_fetched >= freshness_cutoff:
            cache_hits.append(record)
        else:
            cache_misses_ids.append(id)

    # Randomly sample if needed
    if len(cache_misses_ids) > settings.STEAM_API_MAX_FETCH_LIMIT:
        cache_misses_ids = random.sample(cache_misses_ids, settings.STEAM_API_MAX_FETCH_LIMIT)

    # If no misses then just return the hits
    if len(cache_misses_ids) == 0:
        return cache_hits

    # Get game details from Steam API async
    # The * is the syntax for unpacking. Basically calling gather(game1, game2, game3, ...)
    fetched_results = await asyncio.gather(
        *[fetch_game_details_from_steam(id) for id in cache_misses_ids],
        return_exceptions = True
    )

    # Insert into db
    for game_details in fetched_results:
        if not game_details or isinstance(game_details, Exception):
            continue

        app_id = game_details["app_id"]
        cached_game = records_by_id.get(app_id)

        if cached_game:
            # Has cache record but stale, needs updating
            cached_game.name = game_details["name"]
            cached_game.image_url = game_details["image_url"]
            cached_game.review_score = game_details["review_score"]
            cached_game.total_reviews = game_details["total_reviews"]
            cached_game.review_score_desc = game_details["review_score_desc"]
            cached_game.developers = game_details["developers"]
            cached_game.publishers = game_details["publishers"]
            cached_game.short_description = game_details["short_description"]
            cached_game.categories = game_details["categories"]
            cached_game.genres = game_details["genres"]
            cached_game.last_fetched = datetime.now(timezone.utc)
        else:
            # Resource doesn't exist, make a new one.
            cached_game = models.GamesCache(
                app_id = game_details["app_id"],
                name = game_details["name"],
                image_url = game_details["image_url"],
                review_score = game_details["review_score"],
                total_reviews = game_details["total_reviews"],
                review_score_desc = game_details["review_score_desc"],
                developers = game_details["developers"],
                publishers = game_details["publishers"],
                short_description = game_details["short_description"],
                categories = game_details["categories"],
                genres = game_details["genres"],
                last_fetched = datetime.now(timezone.utc),
            )
            db.add(cached_game)

        cache_hits.append(cached_game)

    db.commit()
    return cache_hits
    
# endregion