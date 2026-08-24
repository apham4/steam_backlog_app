# Loads and validates environment variables.

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    APP_NAME: str = "Backlog Gamer API"
    STEAM_API_KEY: str = ""
    DEV_STEAM_ID: str = ""
    DEV_USERNAME: str = ""
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")

settings = Settings() # instance to be used in other places