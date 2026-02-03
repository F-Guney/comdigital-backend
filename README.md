# Comdigital Backend Developer Case Study

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Tech Stack

| Layer          | Technology                     |
|----------------|--------------------------------|
| Framework      | FastAPI                        |
| Database       | PostgreSQL + SQLAlchemy 2.0    |
| Auth           | JWT (python-jose) + bcrypt     |
| Validation     | Pydantic v2                    |
| Tests          | pytest + httpx                 |
| Containerisation | Docker + Docker Compose      |

## Quick Start

### SET Environment Variables (create .env file - [.env.example](.env.example))

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Create the Test Database
docker compose exec <container_name> psql -U comdigital -d comdigital_case -c "CREATE DATABASE comdigital_test;"
```

> **Docker note:** When running inside Docker Compose, the app service overrides `DATABASE_URL` with `db` as the hostname instead of `localhost`.

### Seed the Database

```bash
python -m scripts.seed
```

Creates 3 test users and 25 items across 5 categories.

| Email             | Password     |
|-------------------|--------------|
| admin@example.com | admin123456  |
| john@example.com  | john123456   |
| jane@example.com  | jane123456   |

### 6. Run the Server

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8080`. Swagger docs at `http://localhost:8080/docs`.

| Variable                      | Default                      | Description               |
|-------------------------------|------------------------------|---------------------------|
| `DATABASE_URL`                | `postgresql+asyncpg://comdigital:comdigital@db:5432/comdigital_case` | Async database URL   |
| `SECRET_KEY`                  | `secret`                     | JWT signing key           |
| `ALGORITHM`                   | `HS256`                      | JWT algorithm             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                         | Access token TTL (min)    |
| `REFRESH_TOKEN_EXPIRE_MINUTES`| `3600`                       | Refresh token TTL (min)   |
| `DEBUG`                       | `false`                      | Enable SQL echo           |

## Running with Docker Compose (Full Stack)

To run the entire application in containers:

```bash
docker compose up -d --build
```

The API will be available at `http://localhost:8080`.

The app container automatically waits for the database, runs the seed script, and starts the server.

## Running Tests

Make sure PostgreSQL is running and the test database exists (see above).

```bash
pytest -v
```

With coverage: (Open htmlcov/index.html)

```bash
pytest --cov=app --cov-report=html -v
```


## API Endpoints

### Health

| Method | Endpoint  | Description          | Auth |
|--------|-----------|----------------------|------|
| GET    | `/health` | DB connectivity check | No   |

### Users

| Method | Endpoint              | Description              | Auth |
|--------|-----------------------|--------------------------|------|
| POST   | `/api/users/register` | Create account           | No   |
| POST   | `/api/users/login`    | Get access + refresh tokens | No   |
| POST   | `/api/users/refresh`  | Renew access token       | No   |
| GET    | `/api/users/profile`  | Get current user         | Yes  |
| PUT    | `/api/users/profile`  | Update name fields       | Yes  |

### Items

All item endpoints require authentication (`Authorization: Bearer <token>`).

| Method | Endpoint                              | Description         |
|--------|---------------------------------------|---------------------|
| GET    | `/api/items/`                         | List items (paginated) |
| POST   | `/api/items/`                         | Create item         |
| GET    | `/api/items/{id}`                     | Get item by ID      |
| PUT    | `/api/items/{id}`                     | Update item         |
| DELETE | `/api/items/{id}`                     | Soft delete item    |
| GET    | `/api/items/analytics/category-density` | Category analytics  |

### Query Parameters (GET `/api/items/`)

| Param    | Type   | Default      | Description                          |
|----------|--------|--------------|--------------------------------------|
| page     | int    | 1            | Page number (≥ 1)                    |
| per_page | int    | 20           | Items per page (1–100)               |
| status   | string | —            | Filter by status                     |
| category | string | —            | Filter by category                   |
| sort_by  | string | created_at   | Sort field: `created_at` or `name`   |
| order    | string | desc         | Sort order: `asc` or `desc`