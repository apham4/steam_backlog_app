# Loads and validates environment variables.

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    #Steam API
    STEAM_GET_OWNED_GAMES_URL: str = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    STEAM_FETCH_APP_DETAILS_URL: str = "https://store.steampowered.com/api/appdetails/"
    STEAM_FETCH_APP_REVIEWS_URL: str = "https://store.steampowered.com/api/appreviews/{app_id}"
    STEAM_API_KEY: str = ""
    STEAM_API_TIMEOUT_SECONDS: int = 10
    DEV_STEAM_ID: str = ""
    DEV_USERNAME: str = ""

    # FastAPI app
    APP_NAME: str = "Backlog Gamer API"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    CORS_METHODS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]

    # Default Rules
    GAME_CACHE_TTL_DAYS: int = 7
    BACKLOG_THRESHOLD_MINS: int = 60
    RECENT_THRESHOLD_MINS: int = 120
    SKIP_COOLDOWN_DAYS: int = 3

    model_config = SettingsConfigDict(env_file = ".env", extra = "ignore")

settings = Settings() # instance to be used in other places