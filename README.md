# room-manage

Apartment and room rental administration system for a property management company.

## Stack

- Backend: FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL.
- Frontend: Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui-style primitives, Recharts.
- Infrastructure: Docker Compose with backend, frontend, and PostgreSQL.

## Local Docker

```bash
docker compose up --build
```

Docker Compose uses the explicit `room_manage_net` bridge network for service-to-service traffic. Published host ports are only for browser access and local development tools.

Services:

- Frontend: http://localhost:13000
- Backend API: http://localhost:18000
- API health: http://localhost:18000/health
- PostgreSQL: localhost:15432

Seeded local accounts:

```text
admin@example.com / password123
staff@example.com / password123
```

## Backend

```bash
cd backend
pip install -r requirements-dev.txt
alembic upgrade head
python -m scripts.seed
pytest --cov=app
ruff check .
uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
npm run build
npm run start
npm run test
npm run test:e2e
npm run lint
```

`npm run test:e2e` expects the Docker stack to be running and uses:

- `PLAYWRIGHT_BASE_URL` default: http://localhost:13000
- `PLAYWRIGHT_API_BASE_URL` default: http://localhost:18000/api/v1

## Project Guidance

- Main agent rules: `AGENTS.md`
- Project-specific Codex guidance: `.project-codex/`
- Progress tracker: `IMPLEMENTATION_PLAN.md`
