from fastapi import Depends, HTTPException, Request, status
import base64
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from yarapi.core.database import users_collection
from yarapi.models.users import UserInDB
from yarapi.config import config

# --- Configuration ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializer = URLSafeTimedSerializer(config.secret_key)


# --- Password Utilities ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# --- User Retrieval ---
async def get_user(username: str) -> UserInDB | None:
    user_data = await users_collection.objects.find_one({"username": username})
    if user_data:
        user_data["_id"] = str(user_data["_id"])
        return UserInDB(**user_data)
    return None


# --- API Authentication (HTTP Basic) ---
async def get_current_api_user(request: Request) -> UserInDB:
    """
    API auth helper that supports two modes:
    - HTTP Basic via the Authorization header (but does NOT emit the
      WWW-Authenticate header to avoid the browser basic-auth popup).
    - Session cookie (same as web auth) so logged-in web users can access
      API endpoints without providing Basic credentials.

    If neither method yields an authenticated user, we return a
    redirect (303) to /login for browser (text/html) requests or a
    401 for programmatic/API clients.
    """
    # Try HTTP Basic from Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Basic "):
        try:
            b64 = auth_header.split(" ", 1)[1]
            decoded = base64.b64decode(b64).decode("utf-8")
            username, password = decoded.split(":", 1)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication header",
            )

        user = await get_user(username)
        if not user or not verify_password(password, user.hashed_password):
            # Do NOT include WWW-Authenticate header so the browser doesn't
            # trigger the basic auth popup.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        return user

    # Fall back to session cookie (web login)
    user = await get_current_web_user(request)
    if user:
        return user

    # No auth provided. If the request expects HTML, redirect to login.
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )

    # Otherwise, respond with 401 for API clients.
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
    )


# --- Web Authentication (Cookies) ---
async def get_current_web_user(request: Request) -> UserInDB | None:
    session_cookie = request.cookies.get("session")
    if not session_cookie:
        return None
    try:
        # The max_age parameter checks token expiration (e.g., 1 day)
        data = serializer.loads(session_cookie, max_age=86400)
        user = await get_user(data.get("username"))
        if not user:
            return None
        return user
    except (SignatureExpired, BadTimeSignature):
        return None


# --- Permission Logic (Reusable Checks) ---
def has_og_user_privilege(user: UserInDB):
    return "og_user" in user.permissions or "og_admin" in user.permissions


def has_og_admin_privilege(user: UserInDB):
    return "og_admin" in user.permissions


def has_api_user_privilege(user: UserInDB):
    return "api_user" in user.permissions or "og_admin" in user.permissions


# --- API Permission Dependencies ---
async def require_api_user(current_user: UserInDB = Depends(get_current_api_user)):
    if not has_api_user_privilege(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="API access required"
        )
    return current_user


# --- Web Permission Dependencies ---
async def require_web_user(user: UserInDB = Depends(get_current_web_user)):
    if not user or not has_og_user_privilege(user):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )
    return user


async def require_web_admin(user: UserInDB = Depends(get_current_web_user)):
    if not user or not has_og_admin_privilege(user):
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"}
        )
    return user
