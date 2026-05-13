# FastAPI Backend Template

Reusable FastAPI backend template with MySQL persistence.

Project conventions:

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 ORM, Alembic, and asyncmy for MySQL persistence
- uv for dependency and environment management
- External MySQL only
- Dockerfile for the API service only
- Ruff for linting, import sorting, and formatting
- REST-style resource API design for business endpoints

## Setup

Install uv if needed:

```bash
brew install uv
```

Sync dependencies:

```bash
uv sync
```

The project dependency source is `pyproject.toml`; use uv for environment
syncing and command execution.

## Configuration

Configure MySQL through environment variables. MySQL is provided outside this
project and is not managed by this repository.

The API reads process environment variables; it does not auto-load `.env` files.
For local development, start from the example file and export it in your shell:

```bash
cp .env.example .env
set -a
. ./.env
set +a
```

```bash
export APP_NAME="FastAPI Backend Template"
export APP_VERSION=0.1.0
export APP_ENV=development
export DEBUG=true
export DOCS_ENABLED=true
export LOG_LEVEL=INFO
export CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
export CORS_ALLOW_CREDENTIALS=false
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=
export MYSQL_DATABASE=fastapi_backend_template
export MYSQL_CONNECT_TIMEOUT=5
export MYSQL_POOL_SIZE=5
export MYSQL_POOL_RECYCLE_SECONDS=1800
export MYSQL_MAX_OVERFLOW=10
export MYSQL_POOL_TIMEOUT=30
export MYSQL_RETRY_ATTEMPTS=3
export MYSQL_RETRY_DELAY_SECONDS=0.2
```

When the API runs in Docker and MySQL runs on the host machine, use:

```bash
export MYSQL_HOST=host.docker.internal
```

## Run Locally

```bash
uv run uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/health/live`
- `http://127.0.0.1:8000/health/ready`

`/health/live` checks that the API process is alive. `/health/ready` also checks
that MySQL is reachable.

## Database Migrations

SQLAlchemy models live in `app/models/`. Alembic reads the same MySQL
environment variables as the API and writes migration scripts to
`migrations/versions/`. Import new model modules from `app/models/__init__.py`
so Alembic autogenerate can see their metadata.

The template starts without business tables. Add your first model and then
generate the first migration for that project-specific schema.

Create a migration after changing models:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```bash
uv run alembic upgrade head
```

Inspect the current migration state:

```bash
uv run alembic current
```

## API Documentation

FastAPI serves Swagger UI at `/docs`, ReDoc at `/redoc`, and the OpenAPI schema
at `/openapi.json` when `DOCS_ENABLED=true`.

For production, set:

```bash
export APP_ENV=production
export DEBUG=false
export DOCS_ENABLED=false
```

Settings validation rejects `DEBUG=true` or `DOCS_ENABLED=true` when
`APP_ENV=production`, so public production API docs stay disabled by default.

## Adding Business Resources

The default app exposes only system and health endpoints. Add project-specific
resources by creating a route module in `app/api/routes/`, schemas in
`app/schemas/`, models in `app/models/`, repositories in `app/repositories/`,
and business logic in `app/services/`.

Use `get_db_session` for read-only database work. Use `get_db_transaction` for
write endpoints so successful requests commit and exceptions roll back through a
single dependency-managed transaction boundary.

## API Design

Business APIs should follow REST-style resource conventions:

- Model paths around resources, not actions: `/items` and `/items/{item_id}`.
- Use HTTP methods for intent: `GET` reads, `POST` creates, `PUT` or `PATCH`
  updates, and `DELETE` removes.
- Keep `GET` endpoints side-effect free.
- Use query parameters for filtering, sorting, and pagination.
- Return appropriate HTTP status codes and the uniform success and error
  response shapes.
- Treat `/health/*`, `/docs`, `/redoc`, and `/openapi.json` as operational or
  documentation exceptions.

## Project Structure

```text
app/
  main.py                 ASGI entrypoint; keeps app.main:app stable
  api/
    dependencies.py       Shared FastAPI dependency providers
    router.py             Top-level API router composition
    routes/               HTTP route modules grouped by domain
  core/
    application.py        FastAPI app factory and app assembly
    config.py             Environment-backed settings
    exceptions.py         API exception helpers
    errors.py             Uniform error responses
    logger.py             JSON logging configuration
    response_catalog.py   Common API response codes and messages
    request_context.py    Request-scoped context such as request IDs
  middleware/
    setup.py              Middleware composition
    cors.py               CORS middleware configuration
    request_logging.py    Request logging and request ID middleware
  db/
    session.py            SQLAlchemy async engine and session infrastructure
  models/                 SQLAlchemy database model definitions
  repositories/           Future data access layer
  schemas/                Pydantic request/response schemas and API envelopes
  services/               Business logic and dependency health checks
tests/                    Pytest smoke and behavior tests
```

Keep route handlers thin: validate HTTP concerns in `api/routes`, put business
logic in `services`, put reusable FastAPI dependencies in `api/dependencies.py`,
put HTTP middleware in `middleware`, keep database model definitions in `models`,
and isolate persistence logic in `repositories` or `db`.

## Production Basics

- Requests and errors are logged as JSON to stdout.
- Every response includes `X-Request-ID`; pass your own value or the API will
  generate one.
- Successful API responses use a consistent shape:

```json
{
  "code": "success",
  "message": "Success",
  "data": {
    "id": 1,
    "email": "ada@example.com"
  },
  "request_id": "..."
}
```

- Error responses use a consistent shape:

```json
{
  "code": "failed",
  "message": "Request failed",
  "details": {
    "dependency": "mysql",
    "reason": "Error"
  },
  "request_id": "..."
}
```

Common response code/message pairs live in `app/core/response_catalog.py`.
Business responses use only `success`, `invalid`, and `failed` as top-level
codes; route handlers should raise helpers from `app/core/exceptions.py`
instead of spelling out `HTTPException` details inline.

- CORS is disabled unless `CORS_ORIGINS` is set.
- SQLAlchemy MySQL connections use a pool controlled by `MYSQL_POOL_SIZE`.
  Overflow, timeout, and stale-connection handling are controlled by
  `MYSQL_MAX_OVERFLOW`, `MYSQL_POOL_TIMEOUT`, and
  `MYSQL_POOL_RECYCLE_SECONDS`. Readiness checks retry with
  `MYSQL_RETRY_ATTEMPTS` and `MYSQL_RETRY_DELAY_SECONDS`.
- Incoming `X-Request-ID` values are accepted only when they are short
  alphanumeric IDs with `.`, `_`, `:`, or `-`; invalid values are replaced.

## Run With Docker

Build the API image:

```bash
docker build -t fastapi-backend-template .
```

Run the API container:

```bash
docker run --rm -p 8000:8000 \
  -e APP_ENV=production \
  -e DEBUG=false \
  -e DOCS_ENABLED=false \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_PORT=3306 \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD= \
  -e MYSQL_DATABASE=fastapi_backend_template \
  -e MYSQL_CONNECT_TIMEOUT=5 \
  -e MYSQL_POOL_SIZE=5 \
  -e MYSQL_POOL_RECYCLE_SECONDS=1800 \
  -e MYSQL_MAX_OVERFLOW=10 \
  -e MYSQL_POOL_TIMEOUT=30 \
  fastapi-backend-template
```

This Dockerfile containerizes only the API service. It does not start or manage
MySQL.

The image runs as a non-root user, includes a Docker healthcheck against
`/health/live`, and contains `alembic.ini` plus `migrations/` so the same image
can run database migrations:

```bash
docker run --rm \
  -e MYSQL_HOST=host.docker.internal \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD= \
  -e MYSQL_DATABASE=fastapi_backend_template \
  fastapi-backend-template \
  .venv/bin/alembic upgrade head
```

If MySQL is not running on the host machine, replace `MYSQL_HOST` with the
external database host.

Stop the container with `Ctrl+C`.

Remove the image if needed:

```bash
docker image rm fastapi-backend-template
```

## Lint And Format

Check lint:

```bash
uv run ruff check .
```

Check formatting:

```bash
uv run ruff format --check .
```

Run type checking:

```bash
uv run basedpyright
```

Run tests:

```bash
uv run pytest
```

Apply formatting and safe fixes:

```bash
uv run ruff format .
uv run ruff check . --fix
```

GitHub Actions CI runs linting, formatting checks, type checking, tests, and a
Docker image build for pull requests and pushes to `main`.

## Agent Guidance

Repository-specific agent instructions live in `AGENTS.md`.

Project-local Codex skill configuration lives in:

```text
.agents/skills/fastapi-backend-template/
```
