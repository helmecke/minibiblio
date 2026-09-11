## Context

See `proposal.md` for motivation. The repository combines a Next.js 16/React 19 frontend with a FastAPI application backed by async SQLAlchemy and PostgreSQL. It has committed npm and uv lockfiles, Alembic migrations, Node 26 and Python 3.14 container builds, and a PostgreSQL 17 development service, but no test runners or pull-request workflow.

The current `npm run lint` invokes `next lint`, which Next.js 16 removed, and the legacy `.eslintrc.json` does not match the direct ESLint CLI configuration now recommended by Next.js. Python contains Ruff configuration but does not declare Ruff or test tooling as project development dependencies. Database engines and session factories are initialized at module import time from `DATABASE_URL`, which constrains test setup ordering.

The existing `catalog-sorting` and `author-catalog-view` specifications provide concrete frontend regression scenarios. Backend routers rely on PostgreSQL-specific UUID types and async sessions, so SQLite would not faithfully exercise the production persistence path.

## Goals / Non-Goals

**Goals:**

- Provide deterministic, non-interactive validation commands suitable for local use and GitHub-hosted runners.
- Cover selected high-value frontend behavior through both pure unit tests and user-visible component tests.
- Exercise FastAPI health, authentication, and catalog behavior through the ASGI application and a real migrated PostgreSQL database.
- Keep test data isolated and guard destructive cleanup from non-test databases.
- Run frontend and backend validation independently so one failure does not suppress diagnostics from the other stack.

**Non-Goals:**

- Achieving comprehensive application coverage or imposing a coverage percentage threshold.
- Adding browser end-to-end testing or running the complete Docker Compose application in CI.
- Changing application APIs, authorization policy, database models, or documented catalog behavior.
- Publishing containers from pull-request CI or restructuring the existing tag publication workflow.
- Making CI success a repository branch-protection rule, which is configured outside the repository.

## Decisions

### Use Vitest and React Testing Library for frontend tests

Vitest will run TypeScript tests with fast non-watch CI execution, while React Testing Library and `user-event` will validate the catalog table's rendered order, accessible sort state, and toggle interaction in jsdom. The Vitest configuration will resolve the existing `@/*` alias and load shared jest-dom matchers.

The catalog ID parser/comparator will move from the large client component into a small framework-independent module. Unit tests will cover chronology, century-pivot, direction, and unsupported-ID rules; component tests will retain responsibility for default order, interaction, accessibility, and preserving state when props change. Author lookup filtering and fetch error handling will similarly be separated from page rendering enough to test without starting Next.js.

Alternatives considered:

- Jest has a larger established ecosystem but requires more transformation and ESM configuration for this Next.js/TypeScript stack.
- Pure component snapshots would be easy to add but would not express the sorting and error semantics in the existing specs.
- Browser end-to-end tests would offer broader confidence but add server orchestration and flakiness before a unit/integration baseline exists.

### Use pytest, pytest-asyncio, and HTTPX against PostgreSQL

Python development dependencies will be declared in a uv dependency group and locked. Async tests will use HTTPX's ASGI transport so requests pass through FastAPI routing, validation, dependency injection, and response serialization without opening a network port.

The test harness will require an explicit test database URL before importing application modules, set `DATABASE_URL` from that value, and override both database dependency callables used by routers. This ordering ensures the globally created engine targets the test database. A session-scoped setup will verify that the database name is explicitly test-designated and that Alembic has produced the expected schema. Per-test cleanup will truncate application tables with cascading behavior so endpoint commits cannot leak data into later tests.

Alternatives considered:

- SQLite was rejected because PostgreSQL UUIDs, enums, SQL behavior, and migrations are part of the production path.
- Mocked sessions remain useful for isolated unit tests but would not validate queries, commits, migrations, or serialization together.
- Wrapping every test in a transaction is faster, but endpoints explicitly commit and async savepoint restoration is more complex. Truncation is simpler for an initial suite and acceptable at this scale.
- Creating tables directly from SQLAlchemy metadata was rejected because it would allow broken Alembic migrations to pass CI.

### Seed a representative suite rather than broad shallow coverage

The initial frontend suite will enforce catalog chronology and exact author filtering, including the failure-versus-empty distinction. Backend tests will cover health, password/JWT helpers, first-user registration and login boundaries, authenticated identity lookup, and representative catalog create/read/search/update/delete paths and error responses.

This selection spans pure logic, UI interaction, authentication, HTTP contracts, and persistence while staying small enough to diagnose and maintain. Additional domain suites can build on the same fixtures later.

### Make lockfile-backed checks first-class project commands

Frontend scripts will directly invoke ESLint, TypeScript, Vitest, and the existing Next.js build. ESLint will use a flat configuration based on Next.js core-web-vitals and TypeScript rules because `next lint` is unavailable in Next.js 16.

Python lint and test dependencies will live in the uv development group so `uv sync --frozen` reproduces the environment from `uv.lock`. CI will never update either lockfile. No initial coverage gate will be added; a threshold should follow measured, stable coverage rather than an arbitrary baseline.

### Use parallel frontend and backend GitHub Actions jobs

A new CI workflow will trigger for pull requests and pushes to `main`. Both jobs will use repository read permission and dependency caches tied to their lockfiles. Superseded runs for the same branch or pull request will be cancelled through a concurrency group.

The frontend job will use Node 26, install with the same peer-dependency option as `Dockerfile.nextjs`, and run lint, type checking, non-watch tests, and the production build. Next.js telemetry will be disabled.

The backend job will use Python 3.14 and PostgreSQL 17 to match the existing containers. It will install the frozen uv environment, wait for the service health check, apply the complete Alembic chain to an empty test database, run Ruff, and run pytest. The connection values will be workflow-local non-secret test credentials.

Keeping jobs independent provides faster parallel feedback and makes required status checks separable. A single sequential job was rejected because it increases latency and can hide backend results behind an early frontend failure.

### Keep validation separate from publication

The existing tag-triggered Docker publication workflow will not be altered. The new workflow has no package write permission and no publication step. This preserves release behavior and prevents pull-request code from receiving elevated package permissions.

## Risks / Trade-offs

- [PostgreSQL cleanup targets the wrong database] -> Require a separate test URL, verify the parsed database name is test-designated, and fail before any truncation when the guard is not satisfied.
- [Global database objects bind before test configuration] -> Establish environment variables at the top of test configuration before importing the FastAPI app or database module, then override every database dependency callable used by routers.
- [Alembic and ORM metadata diverge] -> Build the integration schema exclusively through Alembic and run API operations against that schema.
- [Component tests become brittle because the catalog table contains unrelated dialogs and navigation] -> Assert roles, row content, and accessible sort state rather than implementation markup; mock only framework boundaries such as translation and navigation.
- [Frontend build duplicates some type-check work] -> Retain both because the explicit type check gives focused diagnostics while the production build verifies Next.js compilation and bundling.
- [Truncation makes backend tests slower] -> Accept the small initial cost; move to savepoint-based isolation only if measured runtime warrants the added fixture complexity.
- [Runtime versions on hosted runners lag container tags] -> Configure explicit versions and update CI alongside container version changes rather than relying on runner defaults.
- [Existing lint debt prevents the new gate from passing] -> Treat migration findings as part of enabling the gate, but avoid broad unrelated style rewrites; document any narrowly scoped rule adjustment in implementation review.

## Migration Plan

1. Add and lock frontend and Python development tooling without changing runtime dependencies.
2. Replace the obsolete frontend lint configuration and establish local validation scripts.
3. Add pure frontend helpers and regression tests, preserving existing rendered behavior.
4. Add guarded PostgreSQL fixtures and the initial backend suite, then verify the Alembic chain against an empty test database.
5. Add the CI workflow and validate both jobs on a pull request.
6. Configure the two successful job names as required branch checks manually if repository policy requires enforcement.

Rollback consists of removing the CI workflow, test configuration, tests, and test-only dependencies, and restoring the previous scripts. No production data or schema rollback is required because the change adds no production migration.
