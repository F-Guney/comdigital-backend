import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base
from app.database import engine, get_db
from app.routers.user import router as user_router
from app.routers.item import router as item_router
from app.utils.cache import close_redis
from app.exceptions.handlers import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database connection established")
    yield
    await close_redis()
    await engine.dispose()
    logger.info("Database connection closed")


app = FastAPI(
    title="Comdigital Case Study",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.include_router(user_router)
app.include_router(item_router)


@app.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}
