## 1. Validation Tooling

- [x] 1.1 Add Vitest, jsdom, React Testing Library, jest-dom, and user-event as frontend development dependencies; configure the `@/*` alias and shared test setup, and verify `npm run test:ci` starts and exits non-interactively.
- [x] 1.2 Replace the removed `next lint` integration with a Next.js 16-compatible flat ESLint configuration, add explicit lint and type-check scripts, and verify `npm run lint` and `npm run typecheck` pass.
- [x] 1.3 Add pytest, pytest-asyncio, HTTPX, and Ruff to the uv development dependency group, configure async test execution, update `uv.lock`, and verify `uv sync --frozen` installs the complete validation environment.

## 2. Frontend Regression Suite

- [x] 2.1 Extract catalog ID chronology parsing and comparison into a framework-independent module without changing table behavior, and verify unit tests cover cross-year order, same-year numeric order, the two-digit century pivot, four-digit years, both directions, and deterministic unsupported-ID placement.
- [x] 2.2 Add CatalogTable component tests for descending default order, ascending/descending toggle behavior, accessible `aria-sort`, and direction persistence after rerendering with changed items; verify the focused component test file passes with `npm run test:ci`.
- [x] 2.3 Separate author lookup filtering and request failure handling from page rendering, add tests for URL-encoded names, case-insensitive exact matches, exclusion of broad non-author matches, empty results, and failed requests, and verify the focused author test file passes.
- [x] 2.4 Run the complete frontend validation sequence with locked dependencies and verify lint, type checking, all Vitest tests, and the production Next.js build pass.

## 3. PostgreSQL Test Harness

- [x] 3.1 Add test configuration that requires an explicit PostgreSQL test URL before importing application database modules, maps it to the application connection setting, and verify the suite fails safely when the URL is absent or does not identify a test database.
- [x] 3.2 Add async engine/session and HTTPX ASGI client fixtures that override both FastAPI database dependencies, clean application tables between tests, remove overrides during teardown, and verify records committed in one fixture-driven test are absent from the next.
- [x] 3.3 Apply the complete Alembic chain to an empty PostgreSQL test database and verify pytest can query the resulting application tables without creating them from ORM metadata.

## 4. Backend Regression Suite

- [x] 4.1 Add health endpoint and password/JWT helper tests covering successful responses, valid password verification, rejected passwords, and decodable access-token subjects; verify the focused tests pass.
- [x] 4.2 Add PostgreSQL-backed authentication API tests for first-user registration, disabled later registration, successful and unsuccessful login, authenticated identity lookup, and invalid or missing credentials; verify the focused authentication suite passes with isolated state.
- [x] 4.3 Add PostgreSQL-backed catalog API tests for create, retrieve, list, search, filter, update, delete, generated-ID uniqueness, malformed identifiers, and missing records; verify the focused catalog suite passes with isolated state.
- [x] 4.4 Run the complete backend validation sequence against a freshly migrated PostgreSQL test database and verify Ruff and all pytest tests pass non-interactively.

## 5. GitHub Actions CI

- [x] 5.1 Add a CI workflow triggered by pull requests and pushes to `main`, with read-only contents permission and concurrency cancellation, and verify the parsed workflow contains no package publication step or application secret reference.
- [x] 5.2 Add the independent Node 26 frontend job with npm lockfile caching, frozen installation behavior matching the Next.js container, disabled telemetry, and lint, type-check, test, and build steps; verify the job commands match the locally passing frontend sequence.
- [x] 5.3 Add the independent Python 3.14 backend job with uv lockfile caching and a health-checked PostgreSQL 17 service, then run frozen dependency installation, Alembic migration, Ruff, and pytest with workflow-local test credentials; verify the job commands match the locally passing backend sequence.
- [x] 5.4 Update contributor documentation with the required local frontend and PostgreSQL-backed backend validation commands, including the test-database safety requirement, and verify every documented command corresponds to a configured script or executable command.

## 6. End-to-End Verification

- [x] 6.1 Run all frontend and backend checks from clean lockfile-based environments and verify no tracked lockfile or generated configuration changes after the validation run.
- [ ] 6.2 Open or update a pull request and verify GitHub Actions reports separate successful frontend and backend jobs while the tag-only Docker publication workflow remains untriggered.
