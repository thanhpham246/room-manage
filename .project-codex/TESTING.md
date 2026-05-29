# Testing Guidelines

## TDD Workflow

Use this loop for new behavior:

```text
1. Add or update a failing test for the behavior.
2. Implement the smallest change that makes the test pass.
3. Refactor only when it improves clarity without expanding scope.
4. Run the relevant verification command.
5. Update IMPLEMENTATION_PLAN.md with the verification result.
```

If infrastructure for a test does not exist yet, add the missing test infrastructure as part of the task or record the gap in `IMPLEMENTATION_PLAN.md`.

## Coverage Standards

- Backend application line coverage must be at least 85%.
- Critical backend domains must target at least 90% meaningful coverage:
  - authentication and authorization
  - contracts
  - invoice generation
  - payments and invoice status updates
- Do not lower coverage thresholds to pass.
- Prefer meaningful behavior tests over coverage-only assertions.

## Backend Test Pyramid

Priority order:

```text
service tests -> repository tests -> API tests -> end-to-end smoke tests
```

Backend test expectations:

- Service tests cover business rules without HTTP noise.
- Repository tests cover important filtering, pagination, and persistence behavior.
- API tests cover status codes, request validation, auth, and response shapes.
- Use factories or fixtures for domain setup.
- Keep seed data separate from test data.

Required backend scenarios:

- Login, logout, current user, and role checks.
- Building and room CRUD with search and status filters.
- Tenant CRUD with search.
- Contract creation and room occupancy rules.
- Meter reading validation.
- Monthly invoice batch generation.
- Invoice totals for rent, utilities, fixed services, surcharges, and discounts.
- Partial and full payment behavior.
- Dashboard KPIs and cash-flow aggregates.

## Frontend Test Strategy

Use component tests for UI behavior and Playwright for critical smoke flows.

Frontend test expectations:

- Login screen renders and submits valid credentials.
- Admin layout renders navigation and user menu.
- Dashboard renders API data and empty states.
- Forms validate required fields with Zod messages.
- Tables render loading, empty, error, and populated states.
- Invoice generation flow is covered by an integration or Playwright smoke test.

## Verification Commands

Expected commands after scaffold:

```bash
cd backend
pytest --cov=app
ruff check .

cd frontend
npm run test
npm run lint

docker compose config
```

Run the smallest relevant command while developing, then run broader verification before marking the implementation phase complete.
