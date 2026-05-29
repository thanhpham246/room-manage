#!/usr/bin/env sh
set -eu

alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000
