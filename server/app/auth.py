# Authentication with Steam API. Will be mock data first.

from sqlalchemy.orm import Session
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

    user = db.query(models.User).filter(models.User.steam_id == settings.DEV_STEAM_ID).first()
    if not user:
        # Create a new user
        user = models.User(
            steam_id = settings.DEV_STEAM_ID,
            username = settings.DEV_USERNAME,
            avatar_url = "",
        )
        # db.add(user)

        # With default user settings
        user_settings = models.UserSettings(user_id = user.id)
        # db.add(user)
        
        # db.commit()
        # db.refresh(user)
    
    return user