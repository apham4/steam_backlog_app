# This is for JWT generation and Steam signature validation (OpenID authentication)

import httpx
import jwt
import re # regex
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.config import settings

# user_id relative to this app, corresponding to a steam_id from Steam.
def create_access_token(user_id: int, steam_id: str) -> str:
    """Encode user identity into a signed JWT string with expiration time."""
    expire = datetime.now(timezone.utc) + timedelta(days = settings.JWT_EXPIRATION_DAYS)
    payload = {
        "sub": str(user_id), # standard subject field to identify the user
        "steam_id": steam_id,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm = settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies signature and returns decoded payload."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms = [settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# This will be used to extract the user's 64bit Steam ID from the response URL returned during Steam OpenID authentication.
STEAM_ID_REGEX = re.compile(r"^https://steamcommunity\.com/openid/id/(\d{17,25})$")

# OpenID 2.0 verification requires re-sending all query parms back to Steam
# overriding 'openid.mode' with 'check_authentication'.
# 1. When user logs in via Steam, app redirects to Steam login page.
# 2. In the login request, the server provides a callback URL to Steam and says "when the user is done, redirect their browser to this callback URL" 
# 3. After login approved, Steam responds with a 302 (redirect) pointing to the callback URL, with OpenID query params appended. Browser follows it because it's talking to just Steam in a different tab.
# 4. Browser runs the callback URL, which makes a request with the server and sends over all the OpenID query params to it.
# 5. Now the server has the query params, verifies them with Steam, and uses them for authenticated actions.
async def verify_steam_openid(query_params: Dict[str, str]) -> Optional[str]:
    """Validates Steam's OpenID assertion params by calling back to Steam.
    Returns 64bit Steam ID if authentic, None if not."""

    validation_params = dict(query_params) # Avoid mutating original query_params (dicts are passed by ref)
    validation_params["openid.mode"] = "check_authentication"

    async with httpx.AsyncClient(timeout = settings.STEAM_API_TIMEOUT_SECONDS) as client:
        response = await client.post(settings.STEAM_OPENID_URL, data = validation_params)
        if response.status_code != 200 or "is_valid:true" not in response.text:
            return None

    # Extract 64bit Steam ID from claimed_id
    # claimed_id = the URI that represents the identity the user claims to control.
    claimed_id = query_params.get("openid.claimed_id", "")
    match = STEAM_ID_REGEX.match(claimed_id)
    return match.group(1) if match else None