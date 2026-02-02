import logging
import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.handlers import NotFoundException
from app.models.item import Item
from app.schemas.item import CreateItemRequest, UpdateItemRequest

logger = logging.getLogger(__name__)

_SORT_COLUMNS = {
    "created_at": Item.created_at,
    "name": Item.name,
}


def _alive():
    """Filter condition excluding soft-deleted items."""
    return Item.deleted_at.is_(None)


async def create_item(
    session: AsyncSession,
    data: CreateItemRequest
) -> Item:
    """Creates an item"""
    item = Item(**data.model_dump())
    session.add(item)
    await session.flush()
    logger.info("Item created: %s", item.id)
    return item


async def get_item_by_id(
    session: AsyncSession,
    item_id: uuid.UUID,
) -> Item:
    query = select(Item).where(Item.id == item_id)
    result = await session.execute(query)
    item = result.scalar_one_or_none()

    if not item:
        raise NotFoundException("Item")

    return item


async def update_item(
    session: AsyncSession,
    item_id: uuid.UUID,
    data: UpdateItemRequest,
) -> Item:
    item = await get_item_by_id(session, item_id)
    updated_data = data.model_dump(exclude_unset=True)

    for key, value in updated_data.items():
        setattr(item, key, value)

    await session.flush()
    logger.info("Item updated: %s", item.id)
    return item


async def delete_item(session: AsyncSession, item_id: uuid.UUID) -> None:
    item = await get_item_by_id(session, item_id)
    item.deleted_at = datetime.now()
    await session.flush()
    logger.info("Item deleted: %s", item.id)


async def get_items(
    session: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    status: str | None = None,
    category: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> tuple[list[Item], int]:
    """List items with pagination & sorting & filtering"""
    base = _alive()
    filters = [base]

    if status:
        filters.append(Item.status == status)
    if category:
        filters.append(Item.category == category)

    count = select(func.count(Item.id)).where(*filters)
    total = (await session.execute(count)).scalar() or 0

    sort = _SORT_COLUMNS.get(sort_by, Item.created_at)
    order = sort.desc() if order == "desc" else sort.asc()

    offset = (page - 1) * per_page
    query = (
        select(Item)
        .where(*filters)
        .order_by(order)
        .offset(offset)
        .limit(per_page)
    )

    result = await session.execute(query)
    items = list(result.scalars().all())

    return items, total


async def get_category_density(
    session: AsyncSession,
):
    query = (
        select(Item.category, func.count(Item.id).label("count"))
        .where(_alive())
        .group_by(Item.category)
        .order_by(func.count(Item.id).desc())
    )

    result = await session.execute(query)
    rows = result.all()

    total = sum(row.count for row in rows)

    categories = [
        {
            "category": row.category,
            "count": row.count,
            "percentage": round((row.count / total) * 100, 1) if total > 0 else 0,
        }
        for row in rows
    ]

    return {"total_items": total, "categories": categories}
