# Anti-Patterns

## Backend

| DO NOT | DO |
| --- | --- |
| Put business rules in FastAPI routers. | Put business rules in services and keep routers thin. |
| Return SQLAlchemy models directly from endpoints. | Return explicit Pydantic response schemas. |
| Reuse ORM models as request schemas. | Keep models and schemas separate. |
| Write raw SQL for normal CRUD without a clear reason. | Use SQLAlchemy repositories for persistence. |
| Let services import routers. | Keep dependency direction `router -> service -> repository`. |
| Mix database commits across random helper functions. | Keep transaction boundaries explicit in services or unit-of-work style dependencies. |
| Add broad exception handlers that hide failures. | Handle expected domain errors explicitly and let unexpected errors fail loudly. |
| Store money as floats. | Use integer VND amounts or `Decimal` with clear precision. |
| Hard-code secrets or credentials. | Read secrets from settings and environment variables. |
| Add generic abstractions before duplication exists. | Write the direct implementation first. |

## Frontend

| DO NOT | DO |
| --- | --- |
| Scatter `fetch` calls across pages and components. | Keep API calls in `lib/api/`. |
| Put complex feature logic inside route files. | Move feature-specific logic into `features/`. |
| Create a card-heavy marketing page for the admin app. | Build the actual admin dashboard as the first screen. |
| Use oversized hero typography inside dense admin panels. | Use compact, scannable admin UI typography. |
| Build one-off UI controls when a shared primitive exists. | Reuse small primitives from `components/ui/`. |
| Store JWT tokens in localStorage. | Use HttpOnly cookies for auth. |
| Show unvalidated forms. | Use React Hook Form with Zod validation. |
| Hide loading, empty, or error states. | Add clear states for lists, forms, and dashboards. |
| Use client components for everything. | Use client components only for interactivity. |

## Testing And Delivery

| DO NOT | DO |
| --- | --- |
| Implement behavior before defining a test case. | Follow TDD for new behavior. |
| Mark checklist items done without verification. | Record the verification command or pending reason. |
| Lower coverage thresholds to pass CI. | Improve tests or simplify implementation. |
| Skip service tests for business rules. | Test business rules at the service layer first. |
| Depend on manual browser checks only. | Add automated tests for critical flows. |
| Refactor unrelated code while implementing a task. | Keep changes surgical and report unrelated issues separately. |
