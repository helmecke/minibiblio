# MiniBiblio Fullstack Template

This repository now ships a dual-stack starter composed of a FastAPI backend and a Next.js frontend. Both apps expose baseline login flows for **patrons** and **librarians** so you can wire authentication, persistence, and UI polish without starting from scratch.

## Project Layout

- `backend/`: FastAPI application with login and admin-auth endpoints, JWT issuance, and in-memory seed users.
- `frontend/`: Next.js application showcasing login form templates, local session storage, and a guarded admin dashboard stub.

## Backend Quickstart

```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --reload
```

Environment toggles live in `backend/app/config.py`. Duplicate the defaults into `.env` if you want secrets outside version control.
At minimum set a unique `MINIBIBLIO_JWT_SECRET` and `MINIBIBLIO_PASSWORD_SALT` before deploying.

## Frontend Quickstart

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` in `.env.local` if the API runs somewhere other than `http://localhost:8000`.
When both apps are running, the default login endpoints live at `http://localhost:8000/auth/login` and `http://localhost:8000/auth/admin/login`.

## Seed Credentials

- Patron login (user portal): `patron / patron123`
- Librarian login (admin portal): `librarian / library123` — token cached in `localStorage` for demo navigation

Swap the in-memory store in `backend/app/users.py` with a persistence layer when you integrate a database or identity provider.

## Next Steps

- Replace token storage with a secure session strategy that matches your hosting plan.
- Harden the admin dashboard by exchanging real metrics for the placeholder copy.
- Add automated tests: Pytest for backend flows, Playwright or Cypress for UI validation.
