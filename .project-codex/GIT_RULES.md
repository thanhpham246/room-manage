# Git Rules

## Branch Naming

Use short lowercase branch names:

```text
feat/<scope>-<summary>
fix/<scope>-<summary>
test/<scope>-<summary>
docs/<scope>-<summary>
chore/<scope>-<summary>
```

Examples:

```text
feat/backend-auth
feat/frontend-dashboard
fix/invoice-payment-status
docs/project-guidelines
```

## Commit Format

Use Conventional Commit style:

```text
<type>(<scope>): <description>
```

Allowed types:

- `feat`
- `fix`
- `test`
- `docs`
- `refactor`
- `chore`
- `ci`

Examples:

```text
feat(auth): add cookie-based login
test(invoice): cover monthly batch generation
docs(agent): split project guidance
```

## Commit Rules

- Keep commits focused on one logical change.
- Do not mix formatting-only changes with behavior changes unless the formatter is required for the touched files.
- Do not commit generated caches, local `.env` files, or build artifacts.
- Do not rewrite user changes.
- Do not run destructive commands such as `git reset --hard`, `git checkout --`, or force pushes unless explicitly requested.

## Pull Request Checklist

Before opening or marking a PR ready:

- Update `IMPLEMENTATION_PLAN.md`.
- Run backend tests and lint when backend files changed.
- Run frontend tests and lint when frontend files changed.
- Run Docker Compose verification when infrastructure changed.
- Add or update tests for new behavior.
- Note any verification that could not be run and why.

Expected verification commands after scaffold:

```bash
cd backend
ruff check .
pytest --cov=app

cd frontend
npm run lint
npm run test

docker compose config
docker compose up --build
```
