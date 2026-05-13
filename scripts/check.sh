#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run basedpyright
uv run python -c "from app.main import app; print(app.title)"
uv run pytest

if [[ "${CHECK_DOCKER_BUILD:-0}" == "1" ]]; then
  docker build -t fastapi-backend-template .
fi
