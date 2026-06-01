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

- [x] Split room UI flow into separate list, create, detail, and edit pages.
  - Verification: `/rooms` no longer contains an inline create form; `/rooms/create`, `/rooms/{id}`, and `/rooms/{id}/edit` build and pass Playwright smoke.
- [x] Add room code generated from building code and room name.
  - Verification: backend auto-generates codes like `HOUSE-001-101` for building-generated rooms and room create API; `pytest --cov=app` covers code creation and code update when room name changes.
- [x] Expand room metadata.
  - Verification: migration and API tests cover room type, max occupants, status values `vacant`, `occupied`, `reserved`, `maintenance`, `unavailable`, area, rent price, deposit amount, and note; `ruff check .` and `pytest --cov=app` pass.
- [x] Keep building-generated rooms as the primary workflow.
  - Verification: backend tests confirm building creation still auto-generates rooms; Playwright opens and edits a generated room from the building detail tree.
- [x] Add optional manual room creation under a floor.
  - Verification: backend create API requires building and floor and rejects floors from another building; Playwright creates one extra room under an existing floor.
- [x] Add room list filters and summary columns.
  - Verification: API and UI support filters by building, floor, status, room type, and search by code/name; Playwright verifies filtered room search by building/status/name, and the UI shows the summary columns.
- [x] Add room detail dashboard.
  - Verification: API tests cover room info, current tenant, active contract dates, current debt, last payment, latest meter readings, and notes; Playwright opens the room detail dashboard after generated-room edit and manual-room create.
- [x] Add room edit workflow.
  - Verification: API tests cover metadata, price, deposit, max occupants, status, and note updates without changing contract data; Playwright updates room name, type, max occupants, status, and note.
- [x] Update contract/billing reads to support room detail.
  - Verification: `pytest --cov=app` covers active contract lookup, debt calculation, latest payment, and latest meter readings for one room.
- [x] Update seed data for upgraded room management.
  - Verification: seed script backfills room codes, room type, max occupants, and statuses idempotently; Docker rebuild ran migrations and seed successfully.
- [x] Run backend verification for Phase 8.
  - Verification: `python -m compileall app scripts alembic`, `ruff check .`, and `pytest --cov=app` pass; coverage reached 90.12%.
- [x] Run frontend verification for Phase 8.
  - Verification: `npm run lint`, `npm run test`, `./node_modules/.bin/tsc --noEmit`, and `npm run build` pass.
- [x] Run Docker and Playwright verification for Phase 8.
  - Verification: `docker compose config` succeeds; `docker compose up --build -d` succeeds; backend health, frontend login, dashboard redirect, seeded admin login, and `npm run test:e2e` pass.

## Phase 9: Modular Backend Architecture And Building Edit UX Rules

- [x] Add modular backend layout for buildings and rooms.
  - Verification: `python -m compileall app scripts alembic`, `ruff check .`, and `pytest --cov=app` pass after moving building/room routers, schemas, services, and repositories under `app/modules`; coverage reached 89.51%.
- [x] Preserve existing `/api/v1` public API paths and response shapes after modularization.
  - Verification: backend API tests pass unchanged with `pytest --cov=app`.
- [x] Update project architecture guidance for modular backend layout.
  - Verification: `.project-codex/ARCHITECTURE.md` documents `app/modules/{domain}` and compatibility exports.
- [x] Enforce Building edit locks in backend.
  - Verification: `pytest --cov=app` covers locked `code` after rooms exist, locked `house_type` with active contracts, and editable operational fields with active contracts.
- [x] Update Building edit UI for locked fields.
  - Verification: Playwright confirms seeded active-contract building disables `Mã nhà` and `Loại nhà`; frontend lint, test, typecheck, and build pass.
- [x] Replace fixed amenity checkbox edit UI with custom Add/Remove text rows.
  - Verification: backend duplicate validation test passes; Playwright creates and edits custom amenities.
- [x] Simplify common monthly expense UI to name and amount only.
  - Verification: backend defaults category to `common` when omitted; Playwright adds a common expense with only name and amount and verifies it on detail.
- [x] Run backend verification for Phase 9.
  - Verification: `python -m compileall app scripts alembic`, `ruff check .`, and `pytest --cov=app` pass; coverage reached 90.07%.
- [x] Run frontend verification for Phase 9.
  - Verification: `npm run lint`, `npm run test`, `./node_modules/.bin/tsc --noEmit`, and `npm run build` pass.
- [x] Run Docker and Playwright verification for Phase 9.
  - Verification: `docker compose config`, `docker compose up --build -d`, backend health, frontend login, dashboard redirect, seeded admin login, and `npm run test:e2e` pass.

## Phase 10: PostgreSQL Search Index Optimization

- [x] Add TDD coverage for normalized Building and Room search behavior.
  - Verification: targeted tests failed before implementation, then `./.venv/bin/pytest tests/test_property_flow.py -k "room_crud_supports_building_filter or building_update_replaces_metadata" --no-cov` passed.
- [x] Add PostgreSQL `pg_trgm` migration and GIN trigram indexes for Building and Room search text.
  - Verification: Docker PostgreSQL query confirmed `pg_trgm`, `ix_buildings_search_trgm`, and `ix_rooms_search_trgm` exist after `docker compose up --build -d`.
- [x] Update Building and Room repositories to use normalized indexed search expressions instead of per-column `ILIKE` chains.
  - Verification: Docker API checks returned one result for normalized building search `nguyen   trai` and normalized room search `house-001-101`.
- [x] Run backend verification for Phase 10.
  - Verification: `./.venv/bin/python -m compileall app scripts alembic`, `./.venv/bin/ruff check .`, and `./.venv/bin/pytest --cov=app` pass; coverage reached 90.19%.
- [x] Update architecture guidance with PostgreSQL search/index rules.
  - Verification: `.project-codex/ARCHITECTURE.md` documents indexed normalized search expressions and `pg_trgm` GIN indexes for Building and Room search.

## Phase 11: Tenant Management Upgrade

- [x] Add Phase 11 tenant module checklist to `IMPLEMENTATION_PLAN.md`.
  - Verification: document updated before implementation.
- [x] Move tenant backend code into modular `app/modules/tenants/` layout with compatibility exports.
  - Verification: `./.venv/bin/python -m compileall app scripts alembic`, `./.venv/bin/ruff check .`, and `./.venv/bin/pytest --cov=app` pass; `.project-codex/ARCHITECTURE.md` includes the tenants module.
- [x] Expand tenant data model and migration for generated immutable tenant code, profile fields, emergency contact fields, and soft delete.
  - Verification: Docker PostgreSQL shows Alembic revision `202606010001` with `ix_tenants_search_trgm`, `ix_tenants_tenant_code`, and `uq_tenants_identity_number_active`.
- [x] Add tenant service rules for auto-generated `tenant_code`, duplicate identity validation, active-contract identity edit warning metadata, and soft delete.
  - Verification: `./.venv/bin/pytest tests/test_tenant_flow.py --no-cov` failed before implementation and passes after implementation.
- [x] Add tenant list/detail/create/update/delete API endpoints with search, status filters, and deleted filters.
  - Verification: `./.venv/bin/pytest tests/test_tenant_flow.py --no-cov` passes; Docker API search `GET /api/v1/tenants?search=TENANT-001` returns the seeded tenant.
- [x] Update contract creation to reject soft-deleted tenants.
  - Verification: `test_active_tenant_detail_identity_warning_and_contract_rejects_deleted_tenant` passes.
- [x] Add tenant frontend list, create, detail, and edit pages with separate screens and identity edit warning.
  - Verification: `npm run lint`, `npm run test`, `./node_modules/.bin/tsc --noEmit`, and `npm run build` pass; Docker frontend `GET /tenants` returns 200 after login.
- [x] Run backend verification for Phase 11.
  - Verification: `./.venv/bin/python -m compileall app scripts alembic`, `./.venv/bin/ruff check .`, and `./.venv/bin/pytest --cov=app` pass; coverage reached 90.36%.
- [x] Run frontend verification for Phase 11.
  - Verification: `npm run lint`, `npm run test`, `./node_modules/.bin/tsc --noEmit`, and `npm run build` pass.
- [x] Run Docker and Playwright verification for Phase 11.
  - Verification: `docker compose config`, `docker compose up --build -d`, backend health, seeded admin login, tenant API search, authenticated frontend `/tenants`, and `npm run test:e2e` pass.

## Phase 12: Asset-Aware Contract Management Upgrade

- [x] Add Phase 12 contract module checklist to `IMPLEMENTATION_PLAN.md`.
  - Verification: document updated before implementation.
- [x] Add TDD coverage for generated contract code, room contracts, whole-building contracts, pending/reserved status, overlap validation, and invoice locks.
  - Verification: `./.venv/bin/pytest tests/test_contract_flow.py --no-cov` failed before implementation and passes after implementation.
- [x] Move contract backend code into modular `app/modules/contracts/` layout with compatibility exports.
  - Verification: `./.venv/bin/python -m compileall app scripts alembic`, `./.venv/bin/ruff check .`, and `./.venv/bin/pytest --cov=app` pass; `.project-codex/ARCHITECTURE.md` includes the contracts module.
- [x] Expand contract data model and migration for generated immutable contract code, `scope`, `building_id`, nullable `room_id`, and soft delete.
  - Verification: Docker PostgreSQL shows Alembic revision `202606010002`; `contracts.contract_code`, `contracts.scope`, `contracts.building_id`, nullable `contracts.room_id`, and `contracts.deleted_at` exist.
- [x] Expand invoice data model and migration for direct `building_id` and nullable `room_id`.
  - Verification: Docker PostgreSQL confirms `invoices.building_id` is not nullable and `invoices.room_id` is nullable.
- [x] Enforce contract service rules for room vs whole-building scope, asset date overlap, pending/active status, room reserved/occupied updates, and monthly rent lock after invoices.
  - Verification: `tests/test_contract_flow.py` covers overlap rejection, adjacent contract creation, room reserved status, room release on pre-invoice update, and monthly rent lock after invoice creation.
- [x] Update billing generation to create invoices with `building_id` for both room and whole-building contracts.
  - Verification: `test_whole_building_contract_blocks_building_overlap_and_generates_invoice` confirms whole-building invoice has `building_id` and `room_id = null`; existing billing tests pass.
- [x] Update dashboard, building, room, and tenant reads for asset-aware contract and invoice relationships.
  - Verification: `./.venv/bin/pytest tests/test_billing_flow.py tests/test_property_flow.py tests/test_tenant_flow.py tests/test_admin_flows.py --no-cov` passes.
- [x] Add contract frontend list, create, detail, and edit pages for asset-aware contracts.
  - Verification: `npm run lint`, `npm run test`, `./node_modules/.bin/tsc --noEmit`, and `npm run build` pass.
- [x] Run backend verification for Phase 12.
  - Verification: `./.venv/bin/python -m compileall app scripts alembic`, `./.venv/bin/ruff check .`, and `./.venv/bin/pytest --cov=app` pass; coverage reached 88.61%.
- [x] Run frontend verification for Phase 12.
  - Verification: `npm run lint`, `npm run test`, `./node_modules/.bin/tsc --noEmit`, and `npm run build` pass.
- [x] Run Docker and Playwright verification for Phase 12.
  - Verification: `docker compose config`, `docker compose up --build -d`, backend health, seeded admin login, contract API search, authenticated frontend `/contracts`, and `npm run test:e2e` pass.

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
- Tenant MVP uses one primary tenant per contract.
- Tenant code is generated by the backend and cannot be edited.
- Identity numbers remain editable with a frontend warning when the tenant has an active contract.
- Delete actions are soft deletes across tenant management.
- Contract code is generated by the backend and cannot be edited.
- Contracts can reserve either one room or one whole building.
- Future contracts use `pending` and reserve the asset.
- A contract cannot overlap another contract on the same room or whole building asset.
- Whole-building invoices attach directly to `building_id`; `room_id` is nullable.
- `monthly_rent` is locked after invoices exist; rent changes are modeled as future contracts.
