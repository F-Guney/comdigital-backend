import uuid

from fastapi import APIRouter, Depends, Query, status as response_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.schemas.item import ItemResponse, CreateItemRequest, UpdateItemRequest
from app.services.item import get_items, create_item, get_item_by_id, update_item, delete_item, get_category_density

router = APIRouter(
    prefix="/api/items",
    tags=["Items"],
)


@router.get("/")
async def list_items(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
    page: int = Query(0, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    category: str | None = Query(None),
    sort_by: str | None = Query("created_at", pattern="^(created_at|name)$"),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    items, total = await get_items(
        db,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        order=order,
        category=category,
        status=status
    )

    return {
        "success": True,
        "data": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "items": [
                ItemResponse.model_validate(i).model_dump() for i in items
            ],
        }
    }


@router.post("/", status_code=response_status.HTTP_201_CREATED)
async def create(
    data: CreateItemRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    item = await create_item(db, data)
    return {
        "success": True,
        "data": ItemResponse.model_validate(item).model_dump(),
    }


@router.get("/{item_id}")
async def get_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    item = await get_item_by_id(db, item_id)
    return {
        "success": True,
        "data": ItemResponse.model_validate(item).model_dump(),
    }


@router.put("/{item_id}")
async def update(
    item_id: uuid.UUID,
    data: UpdateItemRequest,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    item = await update_item(db, item_id, data)
    return {
        "success": True,
        "data": ItemResponse.model_validate(item).model_dump(),
    }


@router.delete("/{item_id}")
async def delete(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    await delete_item(db, item_id)
    return {
        "success": True,
        "message": "Item deleted successfully",
    }


@router.get("/analytics/category-density")
async def category_density(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    result = await get_category_density(db)
    return {
        "success": True,
        "data": result
    }
