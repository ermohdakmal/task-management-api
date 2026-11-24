# Task Management API

A production-style REST API built with Python 3.11+, FastAPI, SQLAlchemy 2.0,
PostgreSQL, Alembic, and Pydantic v2. The code follows Clean Architecture:
HTTP and framework concerns are kept in the API layer, use cases are in services,
and SQL queries are isolated in repositories.

## Architecture

```text
app/api          FastAPI routers and dependency wiring
app/schemas      Pydantic request and response models
app/services     Framework-independent business rules
app/repositories SQLAlchemy database operations
app/models       SQLAlchemy ORM entities
app/core         Configuration, security, and custom exceptions
app/db           SQLAlchemy engine, session, and declarative base
tests            FastAPI TestClient and SQLite test suite
alembic          Database migrations
```

Dependencies point inward: routers depend on services, and services depend on
repository protocols. Services do not import FastAPI or SQLAlchemy.

## Local setup

1. Install Python 3.11+.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Create configuration:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Start PostgreSQL and run migrations:

   ```powershell
   docker compose up -d db
   alembic upgrade head
   ```

6. Run the API:

   ```powershell
   uvicorn app.main:app --reload
   ```

The interactive API documentation is available at `http://localhost:8000/docs`.

## Docker setup

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Run migrations inside the API container before the first use if migrations are
not managed externally:

```powershell
docker compose run --rm api alembic upgrade head
```

## Tests

The test suite uses a separate in-memory SQLite database and FastAPI TestClient:

```powershell
pytest
```

## Endpoints

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/health` | No | API health check |
| POST | `/auth/register` | No | Register a user |
| POST | `/auth/login` | No | Return a JWT access token |
| GET | `/auth/me` | Yes | Return the current user |
| POST | `/tasks` | Yes | Create an owned task |
| GET | `/tasks` | Yes | List owned tasks with pagination, filters, and search |
| GET | `/tasks/{task_id}` | Yes | Retrieve an owned task |
| PATCH | `/tasks/{task_id}` | Yes | Update an owned task |
| DELETE | `/tasks/{task_id}` | Yes | Delete an owned task |

Authentication uses `Authorization: Bearer <token>`.

List query parameters:

- `limit`: 1-100, default 20
- `offset`: 0 or greater, default 0
- `status`: `todo`, `in_progress`, or `done`
- `priority`: `low`, `medium`, or `high`
- `search`: case-insensitive title substring

## Environment variables

See `.env.example`. `DATABASE_URL` should use the PostgreSQL driver
`postgresql+psycopg://...` in production.
