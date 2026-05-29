# Agent System Rules

## Core Instructions

- Communication with the user must be in Vietnamese.
- Every assistant reply must start with `[CODEX_OK]`.
- Code, comments, documentation, commit messages, and technical output must be in English.
- State assumptions before implementation when requirements are ambiguous.
- Keep changes minimal, surgical, and directly tied to the requested task.
- Do not implement speculative features or broad refactors.

## Project Overview

Room management is an apartment and room rental administration system for one property management company.

MVP scope: dashboard, buildings, rooms, tenants, contracts, meter readings, invoices, payments, expenses, and staff administration.

Core stack: FastAPI, Python 3.11+, Pydantic v2, SQLAlchemy 2, Alembic, PostgreSQL, Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui-style components, Recharts, React Hook Form, Zod, and Docker Compose.

## Required Project Reading

Before writing code for a task, read the relevant project guidance:

- Architecture and data flow: [.project-codex/ARCHITECTURE.md](.project-codex/ARCHITECTURE.md)
- Code quality constraints and forbidden patterns: [.project-codex/ANTI_PATTERNS.md](.project-codex/ANTI_PATTERNS.md)
- Git, branch, commit, and PR rules: [.project-codex/GIT_RULES.md](.project-codex/GIT_RULES.md)
- TDD, coverage, and verification rules: [.project-codex/TESTING.md](.project-codex/TESTING.md)

The root `.codex/` path may be a global Codex environment mount. Do not use it for project-owned guidance. Project-specific guidance lives in `.project-codex/`.

## Progress Tracking

- `IMPLEMENTATION_PLAN.md` is the source of truth for implementation progress.
- Before starting a meaningful task, add or confirm the matching checklist item.
- After completing a task, mark its checkbox and add the verification command or the reason verification is pending.
- Do not mark an item complete unless the implementation and its relevant verification are both done.

## Product Defaults

- UI labels are Vietnamese.
- Currency is VND.
- Timezone assumption is Asia/Ho_Chi_Minh.
- Authentication uses email/password with JWT in HttpOnly cookies.
- Roles are `admin` and `staff`.
- MVP excludes tenant portal, public listings, SaaS billing, file uploads, and detailed RBAC unless explicitly requested.
