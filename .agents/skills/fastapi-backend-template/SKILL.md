---
name: fastapi-backend-template
description: Project-specific guidance for the reusable FastAPI backend template repository. Use when Codex modifies this FastAPI app, Python dependencies, Dockerfile-based API containerization, MySQL integration, lint or format configuration, README, AGENTS.md, or project-local .agents skill configuration.
---

# FastAPI Backend Template

## Overview

Follow this repository's local backend conventions when changing code, dependencies, Dockerfile configuration, lint configuration, or documentation. Keep the project focused on a small FastAPI API backed by an external MySQL database.

## Project Defaults

- Use Python 3.12.
- Use FastAPI for the HTTP API.
- Use uv for dependency and environment management.
- Use MySQL as an external service.
- Use Ruff for linting, import sorting, and formatting.
- Use Dockerfile only for the API service.

## Hard Constraints

- Do not add new conda workflows or document conda as the project standard.
- Do not add multi-service Docker orchestration unless the user explicitly asks for it.
- Do not containerize MySQL.
- Do not introduce Black or Flake8 unless the user explicitly asks for them.
- Do not install this skill globally or modify `~/.codex/skills`.
- Keep project-specific skill files under `.agents/skills/fastapi-backend-template/`.

## Standard Commands

Use these commands when the relevant project configuration exists:

```bash
uv sync
uv run uvicorn app.main:app --reload
uv run ruff check .
uv run ruff format --check .
uv run pytest
docker build -t fastapi-backend-template .
docker run --rm -p 8000:8000 -e MYSQL_HOST=host.docker.internal fastapi-backend-template
```

For an import smoke test:

```bash
uv run python -c "from app.main import app; print(app.title)"
```

## Work Rules

- Prefer small, focused changes that match the current project structure.
- Keep README, AGENTS.md, dependency files, Dockerfile, and lint configuration consistent.
- Use environment variables for MySQL configuration.
- Treat MySQL as an externally managed dependency in local and Docker workflows.
- Avoid unrelated refactors while working on project setup or documentation.

## API Rules

- Design business endpoints as REST-style resource APIs.
- Use resource nouns and stable nested resources in paths.
- Avoid action names in paths; express intent with HTTP methods.
- Use `GET` for reads, `POST` for creation, `PUT` or `PATCH` for updates, and
  `DELETE` for removal.
- Keep `GET` endpoints side-effect free.
- Use query parameters for filtering, sorting, and pagination.
- Return appropriate HTTP status codes and the project's uniform success and
  error response shapes.
- Treat `/health/*`, `/docs`, `/redoc`, and `/openapi.json` as operational or
  documentation exceptions.

## Directory Rules

- Keep `app.main:app` as the stable ASGI entrypoint.
- Put application assembly, settings, common API response definitions, API exception helpers, error handlers, request context, and logging configuration in `app/core/`.
- Put HTTP middleware in `app/middleware/` and compose it through `app/middleware/setup.py`.
- Put shared FastAPI dependencies in `app/api/dependencies.py`.
- Put HTTP route modules in `app/api/routes/` and compose them through `app/api/router.py`.
- Put MySQL connection infrastructure in `app/db/`.
- Put database model definitions in `app/models/`.
- Put Pydantic request and response schemas in `app/schemas/`.
- Put business logic and dependency health checks in `app/services/`.
- Put data access logic in `app/repositories/`.
