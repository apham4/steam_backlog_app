# SQLAlchemy ORM database models.

from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "users"

    # users schema
    id = Column(Integer, primary_key = True, index = True)
    steam_id = Column(String(64), unique = True, index = True, nullable = False)
    username = Column(String(255), nullable = False)
    avatar_url = Column(String(512), nullable = True)
    created_at = Column(DateTime(timezone = True), default = datetime.now(datetime.timezone.utc))

    # Relationships
    settings = relationship("UserSettings", back_populates = "user", uselist = False)
    exclusions = relationship("Exclusion", back_populates = "user", cascade = "all, delete-orphan")

    # back_populates links the classes (e.g. User.settings <-> UserSettings.user) in Python memory. Set one and the other is automatically set.
    # uselist True (default) means one-to-many (one User to a list of Settings). False makes it one-to-one.
    # cascade what happens when a parent is deleted. all, delete-orphan means all children (exclusions) are deleted and orphans (no parent) are deleted.

class UserSettings(Base):
    __tablename__ = "user_settings"

    # user_settings schema
    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), unique = True, nullable = False)
    backlog_threshold_mins = Column(Integer, default = 60) # max playtime in minutes for a game to be considered backlog.
    recent_threshold_mins = Column(Integer, default = 60) # min playtime in minutes for a game to be considered recently played.
    skip_cooldown_days = Column(Integer, default = 3) # when a recommendation is skipped, how long until it can be recommended again.

    # Relationships
    user = relationship("User", back_populates = "settings")

class Exclusion(Base):
    __tablename__ = "exclusions"

    # exclusions schema
    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False, index = True)
    app_id = Column(Integer, nullable = False, index = True)
    created_at = Column(DateTime(timezone = True), default = datetime.now(datetime.timezone.utc), nullable = False, index = True) # does this need indexing?
    expires_at = Column(DateTime(timezone = True), nullable = False, index = True) # created_at + UserSettings.skip_cooldown_days.

    # Relationships
    user = relationship("User", back_populates = "exclusions")

class GamesCache(Base):
    __tablename__ = "games_cache"

    # games_cache schema
    app_id = Column(Integer, primary_key = True, index = True) # Steam AppID
    name = Column(String(255), nullable = False)
    image_url = Column(String(512), nullable = True)
    review_score = Column(Integer, nullable = True) # Internal Steam scale corresponding to review_score_desc.
    total_reviews = Column(Integer, nullable = True)
    review_score_desc = Column(String(255), nullable = True) # Human-readable desc like "Very Positive" or "Mixed"
    last_fetched = Column(DateTime(timezone = True), default = datetime.now(datetime.timezone.utc), nullable = False)