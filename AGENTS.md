# AGENTS.md

Repository-local guidance for Codex and other coding agents working on this
FastAPI backend.

## Project Shape

- Python 3.12 FastAPI HTTP API.
- Dependencies, virtualenv, and command execution are managed with uv.
- MySQL is an external dependency configured through environment variables.
- SQLAlchemy 2.0 ORM, Alembic, and asyncmy are used for MySQL persistence.
- Ruff is the formatter, linter, and import sorter.
- The Dockerfile builds the API runtime image and includes Alembic migrations.
- `app.main:app` is the stable ASGI entrypoint.

## Common Commands

Install or sync dependencies:

```bash
uv sync
```

Run the API locally:

```bash
uv run uvicorn app.main:app --reload
```

Lint and check formatting:

```bash
uv run ruff check .
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

Run the import smoke test:

```bash
uv run python -c "from app.main import app; print(app.title)"
```

Create and apply database migrations:

```bash
uv run alembic revision --autogenerate -m "describe change"
uv run alembic upgrade head
```

Build and run the API container:

```bash
docker build -t fastapi-backend-template .
docker run --rm -p 8000:8000 -e MYSQL_HOST=host.docker.internal fastapi-backend-template
```

## API Design

- Design business endpoints as REST-style resource APIs.
- Use resource nouns in paths, such as `/items` and `/items/{item_id}`.
- Express behavior with HTTP methods: `GET` reads, `POST` creates, `PUT` or
  `PATCH` updates, and `DELETE` removes.
- Keep `GET` endpoints side-effect free.
- Use query parameters for filtering, sorting, and pagination.
- Use `get_db_session` for read-only database work and `get_db_transaction`
  for write endpoints that should commit or roll back as one unit.
- Return appropriate HTTP status codes and the project's uniform success and
  error response shapes.
- Treat `/health/*`, `/docs`, `/redoc`, and `/openapi.json` as operational or
  documentation endpoints rather than business resources.

## Directory Layout

- Put app assembly, settings, common API response definitions, API exception
  helpers, error handlers, request context, and logging configuration in
  `app/core/`.
- Put HTTP middleware in `app/middleware/` and compose it through
  `app/middleware/setup.py`.
- Put shared FastAPI dependencies in `app/api/dependencies.py`.
- Put route modules in `app/api/routes/` and compose them in
  `app/api/router.py`.
- Put MySQL connection infrastructure in `app/db/`.
- Put database model definitions in `app/models/`.
- Put Pydantic request and response schemas in `app/schemas/`.
- Put business logic and dependency health checks in `app/services/`.
- Put data access code in `app/repositories/`.

## Change Rules

- Prefer small, focused changes that match the current project structure.
- Read nearby code before changing conventions or moving responsibilities.
- Keep README, dependency configuration, Dockerfile, and agent guidance aligned
  when a change affects project setup or workflow.
- Use environment variables for runtime configuration.
- Avoid unrelated refactors while changing setup, API behavior, or
  documentation.
