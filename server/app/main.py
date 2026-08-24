# FastAPI entrypoint and API CRUD endpoints.

from datetime import datetime, timedelta, timezone
from fastapi import BackgroundTasks, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from app import auth, database, models, schemas
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
def get_current_user(current_user: models.User = Depends(auth.get_current_user)):
    """Get the currently authenticated user."""
    return current_user

# endregion

# region User Settings Endpoints
@app.put("/api/settings", response_model = schemas.UserSettingsOut)
def update_user_settings(settings_data: schemas.UserSettingsUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
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


# FastAPI automatically injects the BackgroundTasks instance into the endpoint function.
@app.get("/api/exclusions", response_model = List[schemas.ExclusionOut])
def get_exclusions(
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db),
):
    """Get the currently authenticated user's exclusion list and also trigger cleanup of expired exclusions."""

    background_tasks.add_task(cleanup_expired_exclusions)

    exclusions = db.query(models.Exclusion).filter(
        models.Exclusion.user_id == current_user.id,
        models.Exclusion.expires_at > datetime.now(timezone.utc),
    ).all()

    return exclusions


@app.post("/api/exclusions", response_model = schemas.ExclusionOut)
def create_exclusion(exclusion_data: schemas.ExclusionCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    """Create an exclusion entry (when user skips a recommended game) for the currently authenticated user."""

    cooldown_days = exclusion_data.cooldown_days if exclusion_data.cooldown_days else current_user.settings.skip_cooldown_days

    exclusion = models.Exclusion(
        user_id = current_user.id,
        app_id = exclusion_data.app_id,
        expires_at = datetime.now(timezone.utc) + timedelta(days = cooldown_days)
    )

    db.add(exclusion)
    db.commit()
    db.refresh(exclusion)

    return exclusion

# endregion