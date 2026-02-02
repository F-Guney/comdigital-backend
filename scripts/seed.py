"""
Seed script — populates the database with sample users and items.
Usage:
    python -m scripts.seed
"""

import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database import async_session, engine
from app.models.base import Base
from app.models.user import User
from app.models.item import Item
from app.utils.security import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123456",
        "first_name": "Admin",
        "last_name": "User",
    },
    {
        "email": "john@example.com",
        "password": "john123456",
        "first_name": "John",
        "last_name": "Doe",
    },
    {
        "email": "jane@example.com",
        "password": "jane123456",
        "first_name": "Jane",
        "last_name": "Smith",
    },
]

ITEMS = [
    {"name": "MacBook Pro 16", "description": "Apple M3 Pro laptop", "category": "electronics", "status": "active"},
    {"name": "iPhone 15 Pro", "description": "Latest Apple smartphone", "category": "electronics", "status": "active"},
    {"name": "Sony WH-1000XM5", "description": "Noise cancelling headphones", "category": "electronics",
     "status": "active"},
    {"name": "Samsung Galaxy S24", "description": "Android flagship phone", "category": "electronics",
     "status": "active"},
    {"name": "iPad Air", "description": "Tablet for everyday use", "category": "electronics", "status": "inactive"},
    {"name": "Dell Monitor 27\"", "description": "4K USB-C monitor", "category": "electronics", "status": "active"},
    {"name": "Logitech MX Master", "description": "Wireless ergonomic mouse", "category": "electronics",
     "status": "draft"},
    {"name": "Levi's 501 Jeans", "description": "Classic straight fit jeans", "category": "clothing",
     "status": "active"},
    {"name": "Nike Air Max 90", "description": "Retro running shoes", "category": "clothing", "status": "active"},
    {"name": "North Face Puffer", "description": "Winter down jacket", "category": "clothing", "status": "active"},
    {"name": "Uniqlo Heattech", "description": "Thermal innerwear", "category": "clothing", "status": "active"},
    {"name": "Adidas Ultraboost", "description": "Performance running shoes", "category": "clothing",
     "status": "inactive"},
    {"name": "Clean Code", "description": "Robert C. Martin — software craftsmanship", "category": "books",
     "status": "active"},
    {"name": "Designing Data-Intensive Apps", "description": "Martin Kleppmann — distributed systems",
     "category": "books", "status": "active"},
    {"name": "System Design Interview", "description": "Alex Xu — interview prep", "category": "books",
     "status": "active"},
    {"name": "The Pragmatic Programmer", "description": "Hunt & Thomas — developer career", "category": "books",
     "status": "draft"},
    {"name": "Dyson V15 Vacuum", "description": "Cordless stick vacuum", "category": "home", "status": "active"},
    {"name": "IKEA KALLAX Shelf", "description": "4x4 cube storage unit", "category": "home", "status": "active"},
    {"name": "Nespresso Vertuo", "description": "Coffee machine", "category": "home", "status": "active"},
    {"name": "Yoga Mat 6mm", "description": "Non-slip exercise mat", "category": "sports", "status": "active"},
    {"name": "Resistance Bands Set", "description": "5-piece band set", "category": "sports", "status": "active"},
    {"name": "Wilson Basketball", "description": "Official size outdoor ball", "category": "sports",
     "status": "inactive"},
    {"name": "Garmin Forerunner 265", "description": "GPS running watch", "category": "sports", "status": "active"},
    {"name": "TRX Suspension Trainer", "description": "Bodyweight training system", "category": "sports",
     "status": "draft"},
    {"name": "Hydro Flask 32oz", "description": "Insulated water bottle", "category": "sports", "status": "active"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            logger.info("Database already seeded, skipping.")
            return

        for user_data in USERS:
            session.add(User(
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                password=hash_password(user_data["password"]),
            ))

        for i, item_data in enumerate(ITEMS):
            session.add(Item(
                name=item_data["name"],
                description=item_data["description"],
                category=item_data["category"],
                status=item_data["status"],
                created_at=datetime.now() - timedelta(hours=len(ITEMS) - i),
            ))

        await session.commit()

    logger.info("Seed complete: %d users, %d items", len(USERS), len(ITEMS))
    for u in USERS:
        logger.info("  %s / %s", u["email"], u["password"])


if __name__ == "__main__":
    asyncio.run(seed())
