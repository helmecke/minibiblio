<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# Repository Guidelines

## Project Structure & Module Organization
The repository contains two top-level applications. `backend/` hosts the FastAPI service with configuration in `app/config.py`, authentication logic under `app/routes/auth.py`, and shared helpers in `app/security.py` and `app/dependencies.py`. The frontend lives in `frontend/`, organised as a Next.js 14 app that uses the `app/` router—login flows sit in `app/login` and `app/admin/login`, while shared UI lives in `components/`. Styling is centralised in `frontend/styles/globals.css`. Keep backend/domain code within `app/` modules and place integration stubs (e.g., database clients) in dedicated subpackages to preserve separation of concerns.

## Build, Test, and Development Commands
The backend uses [uv](https://docs.astral.sh/uv/). From `backend/`, run `uv sync --extra dev` to install dependencies and `uv run uvicorn app.main:app --reload` to start the API. Execute tests with `uv run pytest --asyncio-mode=auto`. The frontend uses Node 18+: install dependencies with `npm install`, start locally via `npm run dev`, build with `npm run build`, and serve using `npm start`. When both apps run locally, the UI expects the API at `http://localhost:8000`; override with the `NEXT_PUBLIC_API_BASE_URL` variable.

## Coding Style & Naming Conventions
Backend modules follow PEP 8 with four-space indentation and descriptive module names (e.g., `dependencies.py`, `schemas.py`). Use Pydantic models for request/response contracts and keep function names action-oriented (`authenticate_user`, `create_access_token`). Password hashing relies on `hashlib.pbkdf2_hmac`; rotate the `MINIBIBLIO_PASSWORD_SALT` secret via environment configuration in production. Frontend code is typed with TypeScript; prefer functional React components and PascalCase file names inside `components/`. CSS classes use kebab-case. Run `next lint` to stay aligned with the default Next.js ESLint configuration.

## Testing Guidelines
Target FastAPI routes with `pytest` and `httpx.AsyncClient` fixtures; store tests under `backend/tests/` mirroring the `app/` structure (`tests/routes/test_auth.py`). Use `pytest --asyncio-mode=auto` when mixing sync and async tests. For the frontend, reach for Playwright or React Testing Library to validate form behaviour and guarded routes; colocate UI tests in `frontend/__tests__/` and run them via `npm test` once configured. Aim for high coverage on authentication flows since they gate both patron and librarian entry points.

## Commit & Pull Request Guidelines
History follows conventional commits (`feat:`, `fix:`, `chore:`). Summaries should stay under 72 characters; expand on context in the body when necessary. Every PR should include a concise description, screenshots or terminal clips for UX changes, and references to issue IDs (e.g., `Closes #42`). Before requesting review, confirm both apps start cleanly, linting passes, and login scenarios succeed with the seed credentials (`patron/patron123`, `librarian/library123`). Document any new environment toggles in the README or inline `.env.example`.
