# For defining error codes instead of error messages. The messages to display are up to the clinet React app.

from enum import Enum

class RecommendationErrorCode(str, Enum):
    NO_GAMES = "NO_GAMES"
    NO_QUALIFYING_BACKLOG = "NO_QUALIFYING_BACKLOG"
    ALL_EXLUDED = "ALL_EXCLUDED"
    FETCH_FAILED = "FETCH_FAILED"