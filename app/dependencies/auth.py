from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions.handlers import InvalidTokenException, TokenExpiredException
from app.models.user import User
from app.services.user import get_user_by_id
from app.utils.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validate token and return user"""
    try:
        payload = decode_token(token)

        if payload.get("type") != "access":
            raise InvalidTokenException()

        user_id = payload.get("sub")

        if not user_id:
            raise InvalidTokenException()
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidTokenException()

    user = await get_user_by_id(db, user_id)

    if not user:
        raise InvalidTokenException()

    return user
