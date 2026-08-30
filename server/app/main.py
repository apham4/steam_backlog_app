# FastAPI entrypoint and API CRUD endpoints.

from datetime import datetime, timedelta, timezone
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app import auth, database, models, recommender, schemas, steam
from app.config import settings
from app.database import Base, engine

# Create tables in PostgreSQL on startup (CREATE TABLE IF NOT EXISTS). In production use Alembic migrations.
Base.metadata.create_all(bind = engine)

app = FastAPI(title = settings.APP_NAME)

app.add_middleware(
    CORSMiddleware, # CORS to allow React frontend to talk to FastAPI app
    allow_origins = settings.CORS_ORIGINS,
    allow_credentials = True,
    allow_methods = settings.CORS_METHODS,
    allow_headers = settings.CORS_HEADERS,
)


# region User Endpoints
@app.get("/api/me", response_model = schemas.UserOut)
def get_me(
    current_user: models.User = Depends(auth.get_current_user),
):
    """Get the currently authenticated user."""
    return current_user

# endregion

# region User Settings Endpoints
@app.put("/api/settings", response_model = schemas.UserSettingsOut)
def update_user_settings(
    settings_data: schemas.UserSettingsUpdate, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(database.get_db),
):
    """Update the currently authenticated user's settings (thresholds preferences)."""

    user_settings = db.query(models.UserSettings).filter(models.UserSettings.user_id == current_user.id).first()
    if not user_settings:
        user_settings = models.UserSettings(user_id = current_user.id)
        db.add(user_settings)

    user_settings.backlog_threshold_mins = settings_data.backlog_threshold_mins
    user_settings.recent_threshold_mins = settings_data.recent_threshold_mins
    user_settings.skip_cooldown_days = settings_data.skip_cooldown_days

    db.commit()
    db.refresh(user_settings)
    return user_settings

# endregion

# region Exclusion Endpoints
def cleanup_expired_exclusions():
    """Helper background task to delete expired exclusions from the database."""
    # This needs its own SessionLocal instance because it's an async background task. The session from the caller may be out of scope and closed by the time this runs.
    db = database.SessionLocal()
    try:
        db.query(models.Exclusion).filter(
            models.Exclusion.expires_at <= datetime.now(timezone.utc)
        ).delete()
        db.commit()
    finally:
        db.close()


def get_exclusions_with_cleanup(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
) -> List[models.Exclusion]:
    """Helper function to get the currently authenticated user's exclusion list and also trigger cleanup of expired exclusions."""
    # This originally happened directly in get_exclusions endpoint, but got split out to be reused by get_next_recommendation
    
    exclusions = db.query(models.Exclusion).filter(
        models.Exclusion.user_id == current_user.id,
        models.Exclusion.expires_at > datetime.now(timezone.utc),
    ).all()

    background_tasks.add_task(cleanup_expired_exclusions)
    
    return exclusions


# FastAPI automatically injects the BackgroundTasks instance into the endpoint function.
@app.get("/api/exclusions", response_model = List[schemas.ExclusionOut])
def get_exclusions(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Get the currently authenticated user's exclusion list and also trigger cleanup of expired exclusions."""
    return get_exclusions_with_cleanup(background_tasks, current_user, db)


@app.post("/api/exclusions", response_model = schemas.ExclusionOut)
def create_exclusion(
    exclusion_data: schemas.ExclusionCreate, 
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(database.get_db),
):
    """Create an exclusion entry (when user skips a recommended game) for the currently authenticated user."""

    cooldown_days = current_user.settings.skip_cooldown_days

    exclusion = models.Exclusion(
        user_id = current_user.id,
        app_id = exclusion_data.app_id,
        created_at = datetime.now(timezone.utc),
        expires_at = datetime.now(timezone.utc) + timedelta(days = cooldown_days),
    )

    db.add(exclusion)
    db.commit()
    db.refresh(exclusion)

    return exclusion

# endregion

# region Steam Integration Endpoints
@app.get("/api/steam/library", response_model = schemas.SteamLibraryOut)
async def get_steam_library(
    current_user: models.User = Depends(auth.get_current_user),
):
    """Fetch the authenticated user's Steam game library, specifically their backlog games and their recently played games."""

    library_details: steam.GameLibraryDetails = await steam.get_game_library_details(current_user)
    if not library_details:
        raise HTTPException(
            status_code = 404, detail = "No games found or the library is private for the given user."
        )

    steam_library = schemas.SteamLibraryOut(
        total_owned = library_details.total_owned,
        backlog = library_details.backlog,
        recently_played = library_details.recently_played,
    )
    return steam_library


@app.get("/api/steam/game/{app_id}", response_model = schemas.GamesCacheOut)
async def get_steam_game_details(
    app_id: int,
    db: Session = Depends(database.get_db),
):
    """Fetch game details given Steam App ID."""

    game_cache = await steam.get_games_details_batch([app_id], db)
    if not game_cache or not game_cache[0]:
        raise HTTPException(
            status_code = 404, detail = "Game not found or is software or DLC."
        )
    return game_cache[0]

# TODO: A cache warm up call for backlog and recent games when the user logs in
# endregion

# region Recommendation Endpoints
@app.get("/api/recommendation/get", response_model = schemas.RecommendationOut)
async def get_next_recommendation(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Get user's library details, take into account exclusions, return a backlog recommendation."""

    exclusions: List[models.Exclusion] = get_exclusions_with_cleanup(background_tasks, current_user, db)
    library_details: steam.GameLibraryDetails = await steam.get_game_library_details(current_user)

    recommendation_data: recommender.RecommendationData = await recommender.get_top_recommendation(library_details, exclusions, db)
    if not recommendation_data:
        raise HTTPException(
            status_code = 404, detail = "Could not generate a recommendation. Make sure backlog has at least one game."
        )

    return schemas.RecommendationOut(
        game_details = recommendation_data.game_details,
        store_url = recommendation_data.store_url,
        trailer_search_url = recommendation_data.trailer_search_url,
        recent_games_referenced = recommendation_data.recent_games_referenced,
        matched_genres = recommendation_data.matched_genres,
    )

# endregion