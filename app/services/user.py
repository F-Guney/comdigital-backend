import logging
import uuid

from jose import ExpiredSignatureError, JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import RegisterUserRequest, UpdateUserRequest
from app.utils.security import hash_password, verify_password, decode_token
from app.exceptions.handlers import (
    DuplicateEmailException,
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException
)

logger = logging.getLogger(__name__)


async def create_user(session: AsyncSession, data: RegisterUserRequest) -> User:
    """Create a new user"""
    query = select(User).where(User.email == data.email)
    result = await session.execute(query)

    if result.scalar_one_or_none():
        raise DuplicateEmailException()

    user = User(
        email=str(data.email),
        first_name=data.first_name,
        last_name=data.last_name,
        password=hash_password(data.password)
    )

    session.add(user)

    try:
        await session.flush()
    except IntegrityError:
        await session.rollback()
        raise DuplicateEmailException()

    return user


async def get_user_by_id(session: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Get a user by id"""
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
    """Validate credentials and returns user"""
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise InvalidCredentialsException()

    logger.info("User logged in: %s", user.email)
    return user


async def refresh_user(session: AsyncSession, token: str) -> User | None:
    """Refresh user by token"""
    try:
        payload = decode_token(token)

        if payload.get("type") != "refresh":
            raise InvalidTokenException()

        user_id = payload.get("user_id")

        if not user_id:
            raise InvalidTokenException()
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidTokenException()

    user = await get_user_by_id(session, user_id)

    if not user:
        raise InvalidTokenException()

    return user


async def update_user(
    session: AsyncSession, user: User, data: UpdateUserRequest
):
    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return user

    for key, value in update_data.items():
        setattr(user, key, value)

    await session.flush()
    logger.info("User updated successfully: %s", user.email)
    return user
