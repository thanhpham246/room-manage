# Room Management MVP Implementation Plan

This file is the source of truth for implementation progress. Update it before starting a task and after verification.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed and verified
- `[!]` Blocked or verification pending

## Working Rules

- Use TDD for new behavior: test first, implementation second, refactor only when needed.
- Keep every change tied to this plan or update this plan before changing scope.
- Do not mark a checklist item complete until the relevant verification is recorded.
- Keep documentation and technical text in English.

## Phase 0: Project Governance

- [x] Update `AGENTS.md` with stack, architecture rules, TDD standards, and progress-tracking rules.
  - Verification: document review completed during setup.
- [x] Create `IMPLEMENTATION_PLAN.md` with implementation phases and verification gates.
  - Verification: document review completed during setup.
- [x] Split project-specific guidance into `.project-codex/` to avoid conflict with the global `.codex/` mount.
  - Verification: `mountpoint .codex` confirmed `.codex` is an environment mount; `.project-codex/` contains architecture, anti-pattern, git, and testing guidance.

## Phase 1: Repository And Infrastructure Scaffold

- [x] Create backend, frontend, and infrastructure directory structure.
  - Verification: `rg --files --hidden -g '!.git/**'` shows backend, frontend, and project guidance layout.
- [x] Add root `docker-compose.yml` with PostgreSQL, backend, and frontend services.
  - Verification: `docker compose config` succeeds and shows `db`, `backend`, and `frontend` attached to `room_manage_net`.
- [x] Add environment examples for backend and frontend.
  - Verification: `.env.example`, `backend/.env.example`, and `frontend/.env.example` are present and match app config.
- [x] Add README setup instructions.
  - Verification: README contains Docker, backend, frontend, test, and seed commands.

## Phase 2: Backend Foundation

- [x] Add FastAPI application factory, settings, CORS, health endpoint, and API v1 router.
  - Verification: backend health tests pass in `pytest --cov=app`.
- [x] Add SQLAlchemy 2 database setup and Alembic migration configuration.
  - Verification: Alembic files and initial schema migration are present; `docker compose up --build -d` starts backend after PostgreSQL is healthy.
- [x] Add base layered structure: routers, schemas, services, repositories, models, dependencies.
  - Verification: `python -m compileall backend/app backend/scripts`, `ruff check .`, and backend tests pass.
- [x] Add test configuration with coverage threshold.
  - Verification: `pytest --cov=app` enforces 85% and reached 92.60%.

## Phase 3: Backend Domain MVP

- [x] Add auth models, password hashing, JWT HttpOnly cookie login/logout, and current-user dependency.
  - Verification: auth API tests pass.
- [x] Add role checks for `admin` and `staff`.
  - Verification: admin-only and authenticated operational routes are covered by API tests.
- [x] Add buildings and rooms CRUD with search, pagination, and status filters.
  - Verification: property flow API tests pass.
- [x] Add tenants CRUD with search and pagination.
  - Verification: tenant creation and list endpoints are covered by API tests.
- [x] Add contracts linking tenants and rooms with active/ended status rules.
  - Verification: contract creation and occupied room update are covered by API tests.
- [x] Add meter readings and manual monthly batch invoice generation.
  - Verification: invoice generation test covers rent, electricity, water, fixed services, surcharges, discounts, and totals.
- [x] Add payments with partial/full payment behavior and invoice status updates.
  - Verification: payment tests cover partial and paid invoice states.
- [x] Add expenses and dashboard aggregate endpoints.
  - Verification: expenses and dashboard summary API tests pass.
- [x] Add seed script for demo admin, sample building, rooms, tenants, contracts, invoices, and payments.
  - Verification: seed script is present and idempotent by lookup; seeded admin login succeeds against the Docker backend.

## Phase 4: Frontend Foundation

- [x] Add Next.js App Router project with TypeScript, Tailwind CSS, and app shell.
  - Verification: `npm run test`, `npm run lint`, and `npm run build` pass.
- [x] Add shadcn/ui-style primitives needed for admin screens.
  - Verification: component smoke tests pass.
- [x] Add API client with cookie-based auth support and typed response handling.
  - Verification: server/client API modules compile in `npm run build`; browser login uses `credentials: include`.
- [x] Add protected admin layout with sidebar, top search, theme toggle placeholder, notification placeholder, and user menu.
  - Verification: `npm run build` compiles all admin routes.

## Phase 5: Frontend Domain Screens

- [x] Add login screen and authenticated redirect behavior.
  - Verification: `/login` returns 200, unauthenticated `/dashboard` redirects to `/login`, and authenticated `/dashboard` returns 200 in Docker.
- [x] Add dashboard with KPI cards, cash-flow chart, occupancy/profit chart, and recent activity panels.
  - Verification: dashboard route builds and uses API fallback empty state.
- [!] Add buildings and rooms screens with table, filters, create/edit forms, and status badges.
  - Verification: routes build and shared table tests pass; dedicated create/edit form tests are pending.
- [!] Add tenants screen with table, search, create/edit forms.
  - Verification: route builds; dedicated form tests are pending.
- [!] Add contracts screen with room assignment and lifecycle status.
  - Verification: route builds; dedicated lifecycle UI tests are pending.
- [!] Add meter readings and invoices screens with monthly batch generation action.
  - Verification: invoices route builds; full generation UI flow test is pending.
- [!] Add payments and expenses screens.
  - Verification: routes build; dedicated payment/expense UI tests are pending.

## Phase 6: End-To-End Verification

- [x] Run backend lint and tests.
  - Verification: `ruff check .` and `pytest --cov=app` pass in `backend`; coverage reached 92.60%.
- [x] Run frontend lint and tests.
  - Verification: `npm run lint`, `npm run test`, `npm run build`, and `npm audit --audit-level=moderate` pass in `frontend`.
- [x] Run Docker Compose stack.
  - Verification: `docker compose up --build -d` succeeds with explicit `room_manage_net`; `docker compose ps` shows `db`, `backend`, and `frontend` running; backend health, frontend login, dashboard redirect, authenticated dashboard, and seeded admin login checks pass.
- [x] Run Playwright smoke flow against Docker stack.
  - Verification: `npm run test:e2e` passes 3 smoke tests covering protected redirect, admin login/dashboard, room creation, and payment recording. Invoice generation UI remains pending because the current button is not wired to a generation action yet.

## Phase 7: House Management Upgrade

- [x] Split building UI flow into separate list, create, detail, and edit pages.
  - Verification: `/buildings` no longer contains an inline create form; `/buildings/create` creates a building and redirects to `/buildings/{id}`; `/buildings/{id}/edit` updates non-structural building data in Playwright.
- [x] Expand building metadata.
  - Verification: migration and API tests cover unique house code, house type, status, owner contact text, responsible manager, phone, email, Zalo, and emergency contact fields.
- [x] Add floor structure and generated rooms.
  - Verification: backend API tests and Playwright create a building with uneven floor room counts and verify generated floors plus rooms such as `101`, `102`, `201`, and `203`.
- [x] Add `manager_id` as responsible manager selected from active staff users.
  - Verification: create/update validation rejects non-staff managers and accepts active staff managers.
- [x] Add building amenities.
  - Verification: checkbox keys `wifi`, `camera`, `elevator`, `shared_washing_machine`, `parking`, and `security` persist on create, read, and update.
- [x] Add recurring building expense templates.
  - Verification: API tests cover create/read/update templates for common building-level monthly expenses such as Wifi, Security, and Cleaning.
- [x] Add per-building dashboard endpoint.
  - Verification: aggregate tests cover total rooms, occupied rooms, vacant rooms, occupancy rate, monthly revenue, debt, and active contracts expiring within the next 30 days.
- [x] Add building tree endpoint.
  - Verification: API tests return floors with nested generated rooms in floor order and room order.
- [x] Add frontend building list page.
  - Verification: `npm run build` compiles list search/filter controls, building rows, and navigation actions for view, edit, and create.
- [x] Add frontend building create page.
  - Verification: Playwright covers required fields, floor setup rows, uneven room counts, amenities, and common expense templates.
- [x] Add frontend building detail dashboard page.
  - Verification: Playwright covers KPI cards and generated floor-room tree; detail page also renders amenities and common expense templates.
- [x] Add frontend building edit page.
  - Verification: Playwright confirms non-structural status and amenity updates persist; destructive floor/room restructuring remains out of scope.
- [x] Update seed data for upgraded house management.
  - Verification: seed script creates demo building metadata, floors, generated rooms, amenities, manager assignment, and common expense templates idempotently during Docker startup.
- [x] Run backend verification for Phase 7.
  - Verification: `ruff check .` and `pytest --cov=app` pass; coverage reached 91.02%.
- [x] Run frontend verification for Phase 7.
  - Verification: `npm run lint`, `npm run test`, and Docker `npm run build` pass.
- [x] Run Docker and Playwright verification for Phase 7.
  - Verification: `docker compose up --build -d` succeeds; `npm run test:e2e` passes 3 smoke tests covering login, building creation with 2 uneven floors, redirect to building detail, generated room tree, edit update, and payment recording.

## Phase 8: Room Management Upgrade

- [!] Split room UI flow into separate list, create, detail, and edit pages.
  - Verification: implemented `/rooms`, `/rooms/create`, `/rooms/{id}`, and `/rooms/{id}/edit`; `npm run lint`, `npm run test`, and `tsc --noEmit` pass. Runtime verification is pending because `npm run build` is blocked by the sandbox Turbopack process/port restriction.
- [x] Add room code generated from building code and room name.
  - Verification: backend auto-generates codes like `HOUSE-001-101` for building-generated rooms and room create API; `pytest --cov=app` covers code creation and code update when room name changes.
- [x] Expand room metadata.
  - Verification: migration and API tests cover room type, max occupants, status values `vacant`, `occupied`, `reserved`, `maintenance`, `unavailable`, area, rent price, deposit amount, and note; `ruff check .` and `pytest --cov=app` pass.
- [!] Keep building-generated rooms as the primary workflow.
  - Verification: backend tests confirm building creation still auto-generates rooms; generated rooms are linked from the building detail tree. Browser verification is pending with Playwright.
- [!] Add optional manual room creation under a floor.
  - Verification: backend create API requires building and floor and rejects floors from another building; `/rooms/create` is implemented. Browser verification is pending with Playwright.
- [!] Add room list filters and summary columns.
  - Verification: API and UI support filters by building, floor, status, room type, and search by code/name; UI shows building, floor, status, rent, deposit, current tenant, active contract, and debt. Browser verification is pending with Playwright.
- [!] Add room detail dashboard.
  - Verification: API tests cover room info, current tenant, active contract dates, current debt, last payment, latest meter readings, and notes; detail page is implemented. Browser verification is pending with Playwright.
- [!] Add room edit workflow.
  - Verification: API tests cover metadata, price, deposit, max occupants, status, and note updates without changing contract data; edit page is implemented. Browser verification is pending with Playwright.
- [x] Update contract/billing reads to support room detail.
  - Verification: `pytest --cov=app` covers active contract lookup, debt calculation, latest payment, and latest meter readings for one room.
- [!] Update seed data for upgraded room management.
  - Verification: seed script backfills room codes, room type, max occupants, and statuses idempotently; `python -m compileall app scripts alembic` passes. Docker seed runtime verification is pending.
- [x] Run backend verification for Phase 8.
  - Verification: `python -m compileall app scripts alembic`, `ruff check .`, and `pytest --cov=app` pass; coverage reached 90.12%.
- [!] Run frontend verification for Phase 8.
  - Verification: `npm run lint`, `npm run test`, and `./node_modules/.bin/tsc --noEmit` pass; `npm run build` is pending because Turbopack is blocked by sandbox process/port restrictions and escalation was rejected by the runtime usage limit.
- [!] Run Docker and Playwright verification for Phase 8.
  - Verification: `docker compose config` succeeds; `docker compose up --build -d` and `npm run test:e2e` are pending because frontend build verification is blocked by the sandbox/escalation limit.

## Current Assumptions

- The project starts as a new repo with no existing application code.
- MVP is for one property management company, not multi-tenant SaaS.
- Billing is generated manually by staff per month after meter readings are entered.
- Auth uses HttpOnly cookies with JWT.
- No file upload in MVP.
- Owner is contact text only, not a login user.
- Responsible manager is selected from active `staff` users.
- Building code is unique.
- Room names are generated by floor number plus sequence, for example `101`, `102`, `201`, and `202`.
- Generated rooms start with status `vacant`.
- Create building asks for default room rent, deposit, and optional area so generated rooms have valid initial values.
- Total rooms is computed from actual rooms.
- Expected rooms is computed from floor setup.
- Floor and room deletion or restructuring is out of scope for Phase 7.
- Room code is generated from `building.code + room.name`.
- Beds for dormitory rooms are out of scope for Phase 8.
- Room statuses are `vacant`, `occupied`, `reserved`, `maintenance`, and `unavailable`.
- Building-generated rooms are the primary workflow; manual room creation is only for adding extra rooms later.
