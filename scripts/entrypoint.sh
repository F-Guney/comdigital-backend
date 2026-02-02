#!/bin/bash
set -e

echo "Waiting for database..."
until /app/.venv/bin/python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

async def check():
    engine = create_async_engine(os.environ['DATABASE_URL'])
    async with engine.begin() as conn:
        await conn.execute(text('SELECT 1'))
    await engine.dispose()

asyncio.run(check())
" 2>/dev/null; do
  echo "DB not ready, retrying in 2s..."
  sleep 2
done

echo "Database is ready!"

echo "Running seed..."
/app/.venv/bin/python -m scripts.seed || echo "Seed skipped"

echo "Starting server..."
exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 80