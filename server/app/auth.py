# Authentication with Steam API. Will be mock data first.

from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException

from app import models
from app.database import get_db
from app.config import settings

# = Depends(get_db) is FastAPI Dependency Injection. It automatically calls get_db() and passes the returned value to the db parameter.
# After this function is done executing, the finally clause in get_db() is executed, closing the database session.
# get_db() returns a generator (because of yield) so it doesn't directly return a Session object. Also, using Depends makes sure the lifecycle stuff (try/finally) is handled.
def get_current_user(db: Session = Depends(get_db)) -> models.User:
    """Get the (currently mock) authenticated user."""

    if not settings.DEV_STEAM_ID:
        raise HTTPException(status_code = 500, detail = "DEV_STEAM_ID not set in .env file.")

    # Eager load the UserSettings associated with this user (done in 1 query).
    user = db.query(models.User).options(joinedload(models.User.settings)).filter(models.User.steam_id == settings.DEV_STEAM_ID).first()

    if not user:
        # If no user, create user and settings in a single transaction.
        user = models.User(
            steam_id = settings.DEV_STEAM_ID,
            username = settings.DEV_USERNAME,
            avatar_url = "",
            settings = models.UserSettings() # making use of relationship specified in models.py to automatically set the foreign key (user_id).
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    elif not user.settings:
        # In case a user exists but somehow does not have settings.
        user.settings = models.UserSettings()
        db.commit()
        db.refresh(user)
    
    return user