# Authentication with Steam API. Will be mock data first.

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, joinedload

from app import models, security
from app.database import get_db
from app.config import settings

# HTTPBearer inspects incoming request for "Authorization: Bearer <token>" header.
# Used as a param for get_current_user. Automatically executed.
# FastAPI automatically injects incoming request objects into this.
security_scheme = HTTPBearer(auto_error = False)

# = Depends(get_db) is FastAPI Dependency Injection. It automatically calls get_db() and passes the returned value to the db parameter.
# After this function is done executing, the finally clause in get_db() is executed, closing the database session.
# get_db() returns a generator (because of yield) so it doesn't directly return a Session object. Also, using Depends makes sure the lifecycle stuff (try/finally) is handled.
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """Verifies JWT from Authorization header and loads the User model for the authenticated user."""

    # auto_error = False means HTTPBearer returns None instead of an exception if Authorization header is absent.
    if not credentials:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Authentication token required.",
            header = {"WWW-Authenticate": "Bearer"},
        )

    # Authorization header is present. If the key is incorrect or expired, decode_access_token returns none, so it needs a new one.
    payload = security.decode_access_token(credentials.credentials) # from security.py
    if not payload:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired authentication token.",
            header = {"WWW-Authenticate": "Bearer"},
        )

    # Eager load the UserSettings associated with this user (done in 1 query).
    user_id = int(payload["sub"])
    user = db.query(models.User).options(joinedload(models.User.settings)).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "User account not found.",
            header = {"WWW-Authenticate": "Bearer"},
        )
    
    return user