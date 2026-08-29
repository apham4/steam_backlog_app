# Pydantic schemas for request/response validation.
# SQLAlchemy models (database.py) are used for database operations, while Pydantic schemas (schemas.py) are used for API input/output contracts (validation, serialization, type safety).

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.config import settings

# Naming conventions for class suffixes:
# Base: parent class containing attributes shared across creation, updates, responses.
# Create: defines the data contract required from client for creating a new resource. Excludes server-managed fields (id, created_at) and can require certain fields.
# Update: same as above but for PUT/PATCH. Usually have all fields optional.
# Out: defines what the client receives in the HTTP response. Can include server-managed fields (id, created_at) with sensitive fields filtered out. Has model_config so Pydantic can read attributes directly from SQLAlchemy ORM objects.

# region UserSettings Schemas
class UserSettingsBase(BaseModel):
    backlog_threshold_mins: int = settings.BACKLOG_THRESHOLD_MINS
    recent_threshold_mins: int = settings.RECENT_THRESHOLD_MINS
    skip_cooldown_days: int = settings.SKIP_COOLDOWN_DAYS


class UserSettingsUpdate(UserSettingsBase):
    pass # all needed fields are in UserSettingsBase


class UserSettingsOut(UserSettingsBase):
    model_config = ConfigDict(from_attributes = True) # allows Pydantic to read from SQLAlchemy model attributes

# endregion

# region Exclusion Schemas
class ExclusionBase(BaseModel):
    app_id: int


class ExclusionCreate(ExclusionBase):
    pass


class ExclusionOut(ExclusionBase):
    id: int
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes = True)

# endregion

# region User Schemas
# User Schemas. Users are created on the server side when a user logs in via Steam API.
class UserOut(BaseModel):
    id: int
    steam_id: str
    username: str
    avatar_url: Optional[str] = None
    settings: Optional[UserSettingsOut] = None
    # we don't need exclusions here because that's only for getting recommendations, and it has its own endpoint.

# endregion

# region Games Cache Schemas
class GamesCacheBase(BaseModel):
    app_id: int
    name: str
    image_url: Optional[str] = None
    review_score: Optional[int] = None
    total_reviews: Optional[int] = None
    review_score_desc: Optional[str] = None
    developers: Optional[List[str]] = None
    publishers: Optional[List[str]] = None
    short_description: Optional[str] = None
    categories: List[str] = []
    genres: List[str] = []


class GamesCacheOut(GamesCacheBase):
    last_fetched: datetime # technically not needed but useful for debugging.

    model_config = ConfigDict(from_attributes = True)

# endregion

# region Steam Library Schemas
# Not a model but useful as a data struct for specifying the shape of response data. Also useful for Swagger UI to know what return data shape to expect.
class SteamOwnedGame(BaseModel):
    appid: int
    name: str
    playtime_forever: int
    playtime_2weeks: Optional[int] = 0


class SteamLibraryOut(BaseModel):
    total_owned: int
    backlog: List[SteamOwnedGame]
    recently_played: List[SteamOwnedGame]

# endregion