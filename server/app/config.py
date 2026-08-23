# Loads and validates environment variables.

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    STEAM_API_KEY: str = ""
    DEV_STEAM_ID: str = ""
    DEV_USERNAME: str = ""

    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")

settings = Settings() # instance to be used in other places