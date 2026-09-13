## Why

MiniBiblio has no automated test command or pull-request validation workflow, so regressions can be merged without verifying the Next.js application, FastAPI behavior, or PostgreSQL migrations. Establishing a repeatable local test suite and CI quality gate makes the existing application requirements enforceable before changes reach `main`.

## What Changes

- Add frontend unit and component tests for catalog sorting and author-specific catalog behavior.
- Add backend unit and PostgreSQL-backed API integration tests for health, authentication, and catalog operations.
- Add deterministic frontend lint, type-check, test, and production-build commands.
- Add deterministic Python lint, migration, and test commands with test dependencies managed by uv.
- Add a GitHub Actions workflow that runs independent frontend and backend jobs for pull requests and pushes to `main`.
- Configure the backend CI job with an isolated PostgreSQL service and apply Alembic migrations before tests.
- Keep tagged Docker image publication separate from pull-request CI.

## Capabilities

### New Capabilities

- `continuous-integration`: Defines the repeatable automated test suites and required GitHub-hosted quality checks for frontend and backend changes.

### Modified Capabilities

None. The existing `catalog-sorting` and `author-catalog-view` behavior is not changed; automated tests will enforce selected scenarios from those capabilities.

## Impact

- Affected configuration includes npm scripts, ESLint, Vitest, pytest, uv development dependencies, and GitHub Actions.
- New tests will exercise Next.js UI behavior and FastAPI endpoints against a dedicated PostgreSQL database.
- CI will install dependencies from `package-lock.json` and `uv.lock`, and will use the Node, Python, and PostgreSQL versions aligned with the existing Docker development and production configuration.
- No public application API or end-user behavior is intentionally changed.
