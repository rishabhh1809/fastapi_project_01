import uuid
from datetime import timedelta
from typing import Optional, Any

import jwt
from passlib.context import CryptContext
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.settings import get_settings
from app.utility import utcnow

settings = get_settings()

# ------------------------------------------------------------------
# 1. Password hashing / verification
# ------------------------------------------------------------------
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return pwd_ctx.verify(plain, hashed)


# ------------------------------------------------------------------
# 2. Access & Refresh token helpers
# ------------------------------------------------------------------
_session_store: dict[str, dict] = {}


def _create_token(
    sub: str,
    scope: str,
    session_id: Optional[str] = None,
    expires_delta: timedelta = timedelta(minutes=15),
    extra: Optional[dict] = None,
) -> str:
    now = utcnow()
    payload = {
        "sub": sub,
        "scope": scope,
        "iat": now,
        "exp": now + expires_delta,
    }
    if session_id:
        payload["sid"] = session_id
    if extra:
        payload.update(extra)
    return jwt.encode(
        payload, settings.security.jwt_secret, algorithm=settings.security.jwt_algorithm
    )


def create_access_token(
    user_id: str,
    email: Optional[str] = None,
    role: str = "user",
    session_id: Optional[str] = None,
) -> str:
    extra = {"email": email, "role": role}
    return _create_token(
        sub=user_id,
        scope="access",
        session_id=session_id,
        expires_delta=timedelta(minutes=settings.security.access_token_expire_minutes),
        extra=extra,
    )


def create_refresh_token(user_id: str) -> str:
    session_id = str(uuid.uuid4())
    token = _create_token(
        sub=user_id,
        scope="refresh",
        session_id=session_id,
        expires_delta=timedelta(days=settings.security.refresh_token_expire_days),
    )
    # Persist the session server-side
    _session_store[session_id] = {
        "user_id": user_id,
        "created_at": utcnow(),
    }
    return token


def revoke_session(session_id: str) -> bool:
    if session_id in _session_store:
        del _session_store[session_id]
        return True
    return False


# ------------------------------------------------------------------
# 3. Token verification
# ------------------------------------------------------------------
def _decode(token: str, scope: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.security.jwt_secret,
            algorithms=[settings.security.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"{scope.capitalize()} token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=f"Invalid {scope} token"
        )

    if payload.get("scope") != scope:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Token scope mismatch"
        )

    if scope == "refresh":
        sid = payload.get("sid")
        if sid not in _session_store:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Session revoked"
            )

    return payload


async def verify_jwt_token(request: Request) -> dict:
    token = _extract_bearer(request)
    return _decode(token, scope="access")


def verify_refresh_token(refresh_token: str) -> dict:
    return _decode(refresh_token, scope="refresh")


# ------------------------------------------------------------------
# 4. Helper functions
# ------------------------------------------------------------------
def _extract_bearer(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Missing Bearer token"
        )
    return auth.split()[1]


# ------------------------------------------------------------------
# 5. FastAPI Dependencies for authentication and authorization
# ------------------------------------------------------------------
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, Any]:
    token = credentials.credentials
    payload = _decode(token, scope="access")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )

    return {
        "user_id": user_id,
        "email": payload.get("email"),
        "role": payload.get("role", "user"),
    }


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict[str, Any]]:
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    async def role_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return current_user

    return role_checker
