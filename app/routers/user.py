from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.services.user import create_user, authenticate_user, refresh_user, update_user
from app.database import get_db
from app.models.user import User
from app.utils.security import create_access_token, create_refresh_token
from app.schemas.user import (
    RegisterUserRequest,
    UserResponse,
    LoginUserRequest,
    TokenResponse,
    RefreshTokenRequest,
    UpdateUserRequest
)

router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterUserRequest, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, data)
    return {
        "success": True,
        "data": UserResponse.model_validate(user).model_dump()
    }


@router.post("/login")
async def login(form_data: LoginUserRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.email, form_data.password)
    tokens = TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )
    return {
        "success": True,
        "data": tokens.model_dump()
    }


@router.post("/refresh")
async def refresh(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    user = await refresh_user(db, data.refresh_token)
    tokens = TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )
    return {
        "success": True,
        "data": tokens.model_dump()
    }


@router.get("/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "success": True,
        "data": UserResponse.model_validate(current_user).model_dump()
    }


@router.put("/profile")
async def update_profile(
    data: UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await update_user(db, current_user, data)
    return {
        "success": True,
        "data": UserResponse.model_validate(user).model_dump()
    }
