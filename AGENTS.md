# AGENTS.md

Repository map for coding agents. Use this file to find the right entrypoints,
commands, and source-of-truth files. Keep onboarding detail in `README.md` and
Codex-specific workflow in `.agents/skills/fastapi-backend-template/SKILL.md`.

## Compass

- Python 3.12 FastAPI app with stable ASGI entrypoint `app.main:app`.
- Python commands and dependency management run through uv.
- MySQL is external and configured from environment variables.
- SQLAlchemy 2.0 ORM, Alembic, and asyncmy are used for persistence.
- The Dockerfile builds the API runtime image only and includes migrations.
- Ruff is the formatter, linter, and import sorter.

## Commands

- Sync dependencies: `uv sync`
- Run locally: `uv run uvicorn app.main:app --reload`
- Lint: `uv run ruff check .`
- Check format: `uv run ruff format --check .`
- Type check: `uv run basedpyright`
- Test: `uv run pytest`
- Full local check: `./scripts/check.sh`
- Import smoke test:
  `uv run python -c "from app.main import app; print(app.title)"`
- Create migration:
  `uv run alembic revision --autogenerate -m "describe change"`
- Apply migrations: `uv run alembic upgrade head`
- Build image: `docker build -t fastapi-backend-template .`
- Run image:
  `docker run --rm -p 8000:8000 -e MYSQL_HOST=host.docker.internal fastapi-backend-template`

Prefer `./scripts/check.sh` as the final local quality gate. Use
`CHECK_DOCKER_BUILD=1 ./scripts/check.sh` after Dockerfile or image behavior
changes.

## Project Map

- `app/main.py`: ASGI entrypoint.
- `app/core/application.py`: app factory and assembly.
- `app/core/config.py`: runtime settings.
- `app/core/errors.py` and `app/core/exceptions.py`: uniform error handling.
- `app/core/response_catalog.py`: shared response codes and messages.
- `app/middleware/`: CORS, request logging, and middleware composition.
- `app/api/dependencies.py`: shared FastAPI dependencies.
- `app/api/router.py`: top-level route composition.
- `app/api/routes/`: HTTP route modules.
- `app/db/session.py`: SQLAlchemy async engine and session infrastructure.
- `app/models/`: SQLAlchemy models imported by Alembic metadata.
- `app/repositories/`: persistence queries.
- `app/schemas/`: Pydantic request/response schemas.
- `app/services/`: business logic and dependency health checks.
- `migrations/versions/`: Alembic revisions.
- `tests/`: smoke, behavior, config, database-session, and API tests.

## Request Path

`app/main.py` -> `create_app()` -> middleware -> `api_router` -> route module
-> service/repository -> database session.

Use `get_db_session` for read-only database work and `get_db_transaction` for
write endpoints that need one commit/rollback boundary.

Keep route handlers thin. Put persistence in repositories and business logic in
services.

## API Landmarks

- Business endpoints are REST-style resource APIs with noun-based paths.
- Express behavior with HTTP methods; keep `GET` endpoints side-effect free.
- Use query parameters for filtering, sorting, and pagination.
- Successful responses should use `api_response`.
- Route handlers should use exception helpers from `app/core/exceptions.py`.
- `/health/*`, `/docs`, `/redoc`, and `/openapi.json` are operational or
  documentation endpoints, not business resources.

## Work Rules

- Prefer small, focused changes that match the current project structure.
- Read nearby code before moving responsibilities or introducing conventions.
- Use environment variables for runtime configuration.
- Keep README, AGENTS.md, dependency files, Dockerfile, and lint configuration
  consistent when setup or workflow changes.
- Keep `.agents/skills/fastapi-backend-template/SKILL.md` aligned when project
  conventions or agent workflow guidance changes.
- Prefer focused tests while iterating; do not require live MySQL for unit tests
  unless the task explicitly asks for integration testing.

## Change Map

- Runtime setting: update `app/core/config.py`, `.env.example`, README/Docker
  examples, and tests together.
- Database model: update `app/models/`, import metadata from
  `app/models/__init__.py`, add an Alembic migration, and cover repository/API
  behavior.
- New resource: add route, schema, service/repository/model as needed, register
  the route in `app/api/router.py`, and add focused tests.
- Check workflow: keep `scripts/check.sh` and `.github/workflows/ci.yml`
  aligned.
- Demo user: example code only; replace or remove it coherently across route,
  schema, model, repository, migration, router registration, and tests.

## Safety Notes

- Do not change the uv, external-MySQL, Ruff, or API-only-Dockerfile defaults
  without an explicit request.
- Do not add conda workflows, containerized MySQL, multi-service Docker
  orchestration, Black, or Flake8 unless explicitly requested.
- Do not treat the demo user resource as production domain code.
- Avoid unrelated refactors while changing setup, API behavior, or
  documentation.
