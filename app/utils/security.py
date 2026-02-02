from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from jose import jwt

from app.database import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    expires = timedelta(minutes=settings.access_token_expire_minutes)
    return _create_token(
        data={"sub": user_id, "type": "access"},
        expires_delta=expires,
    )


def create_refresh_token(user_id: str) -> str:
    expires = timedelta(minutes=settings.refresh_token_expire_minutes)
    return _create_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=expires,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


def _create_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
