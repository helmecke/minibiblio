# Project Context

## Purpose
MiniBiblio is a starter kit for a small-library management system. It ships a FastAPI backend and a Next.js frontend that demonstrate patron and librarian authentication flows, so contributors can extend toward full circulation, cataloguing, and audit capabilities without rebuilding the boilerplate.

## Tech Stack
- Python 3.11+, FastAPI, Uvicorn, Pydantic, python-jose, and standard-library PBKDF2 hashing
- uv (Astral) for Python dependency and runtime management
- TypeScript, Next.js 14 App Router, React 18, ESLint (next/core-web-vitals)
- CSS modules via `frontend/styles/globals.css`
- Node.js 18+ and npm for frontend tooling

## Project Conventions

### Code Style
- Backend follows PEP 8 with type hints; modules remain small and descriptive (`security.py`, `dependencies.py`). Password hashing uses `hashlib.pbkdf2_hmac` with a configurable salt. JWT helpers live in `app/security.py`, and Pydantic models define all request/response contracts.
- Frontend uses strict TypeScript, functional React components, and PascalCase filenames inside `components/`. Route files under `app/` use the Next.js App Router conventions, and CSS utility classes are kebab-case.
- Formatting is enforced with `next lint` on the frontend; backend formatting should respect `black` defaults if applied.

### Architecture Patterns
- Backend is layered by responsibility: `routes/` expose HTTP handlers, `dependencies.py` centralises auth guards, `security.py` handles crypto helpers, and `users.py` seeds an in-memory identity store that should be replaced with real persistence.
- CORS is configured in `app/main.py` to allow the Next.js dev server (`http://localhost:3000`). Configuration pulls from `Settings` in `config.py`, which reads `.env` values prefixed with `MINIBIBLIO_`.
- Frontend separates shared UI (`components/Navigation.tsx`, `components/LoginForm.tsx`) from routed pages (`app/login`, `app/admin/login`, `app/admin/dashboard`). Tokens are cached in `localStorage` purely for demos—migrate to HTTP-only cookies or another secure session strategy before production.

### Testing Strategy
- Backend tests should use `pytest` with `httpx.AsyncClient` to exercise FastAPI routes. Run via `uv run pytest --asyncio-mode=auto` and target high coverage on auth flows.
- Frontend tests can use Playwright or React Testing Library. Add suites under `frontend/__tests__/` or `frontend/app/**/__tests__` and run with `npm test` once configured.
- Continuous integration should run linting, backend tests, and frontend tests before merging.

### Git Workflow
- Use feature branches named `feature/<topic>` or `fix/<issue>`.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `chore:`, etc.) with 72-character summaries.
- Pull requests must describe changes, note testing performed, and reference related issues (e.g., `Closes #42`). Include screenshots or terminal output when UX or API behaviour changes.

## Domain Context
- The system models a small-library workflow. Patrons access the standard portal, while librarians (admins) manage inventory, lending operations, and audit logs.
- Future features include book cataloguing, reader management, loan/return tracking, and reporting. Authentication and role separation underpin these flows.

## Important Constraints
- Backend dependencies must be managed with `uv`; do not introduce alternate Python package managers.
- Secrets (`MINIBIBLIO_JWT_SECRET`, `MINIBIBLIO_PASSWORD_SALT`) must be overridden per environment; defaults are demo-only.
- Avoid storing long-lived tokens in browser storage for production; replace the demo strategy during hardening.
- Keep backend and frontend deployable independently to support varied hosting environments.

## External Dependencies
- Authentication relies on JSON Web Tokens signed with `python-jose`.
- No third-party services are currently integrated; persistence is in-memory. Future integrations may include SQLite/PostgreSQL for the catalog, email providers for notifications, or barcode scanners for circulation—document those as they are added.
