import json
import logging

from redis.asyncio import Redis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

redis_client: Redis | None = None


async def get_redis() -> Redis:
    global redis_client
    if redis_client is None:
        try:
            redis_client = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await redis_client.ping()
        except Exception as e:
            logger.warning("Redis connection error: %s", e)
            redis_client = None
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_cached(key: str) -> dict | None:
    try:
        redis = await get_redis()
        if redis is None:
            return None
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning("Cache get failed: %s", e)
    return None


async def set_cached(key: str, value, ttl: int = 300) -> None:
    try:
        redis = await get_redis()
        if redis is None:
            return
        await redis.set(key, json.dumps(value), ex=ttl)
    except Exception as e:
        logger.warning("Cache set failed: %s", e)


async def invalidate_cache(pattern: str):
    try:
        redis = await get_redis()
        if redis is None:
            return
        keys = await redis.keys(pattern)
        if keys and len(keys) > 0:
            await redis.delete(*keys)
    except Exception as e:
        logger.warning("Cache invalidate failed: %s", e)
