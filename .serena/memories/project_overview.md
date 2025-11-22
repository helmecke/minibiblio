# MiniBiblio - Project Overview

## Purpose
MiniBiblio is a comprehensive library management system for small libraries.

## Features

- **Book Management**: Add, edit, delete, and search books
- **Reader Management**: Manage library members and their information
- **Loan Operations**: Check out and return books, extend loan periods
- **Audit Logging**: Complete audit trail of all library operations
- **Search Interface**: Advanced search across books, readers, and loans
- **Statistics**: Loan statistics and reader activity reports

## Tech Stack

### Frontend
- **Next.js 14** (App Router) - React framework with server components
- **React 18** - UI library
- **TypeScript 5** - Type-safe JavaScript
- **Tailwind CSS 3** - Utility-first CSS framework
- **Shadcn UI** - Component library (Radix UI + Tailwind)

### Backend
- **FastAPI** - Python web framework (accessible at `/api/python/`)
- **Next.js API Routes** - Server-side API endpoints (at `/api/`)
- **NextAuth.js v5** - Authentication with Google OAuth
- **PostgreSQL 17** - Database (via Docker)
- **SQLAlchemy 2.0** - ORM with async support (asyncpg driver)
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation and settings

### Development Tools
- **ESLint** - JavaScript/TypeScript linting
- **uv** - Fast Python package manager
- **concurrently** - Run multiple dev servers
- **Docker Compose** - Database and services

## Architecture

- Admin dashboard at `/admin` (protected by authentication)
- Login page at `/login` with Google OAuth
- FastAPI server mapped to `/api/python/` via Next.js rewrites
- Next.js API routes at `/api/`
- Python dependencies managed via `pyproject.toml` and `uv.lock`

## Database

- PostgreSQL 17 running in Docker (port 5432)
- Test database on port 5433
- Async SQLAlchemy with asyncpg driver
- Alembic for migrations (async-compatible)
- Settings via pydantic-settings from `.env` file

### Database Commands
```bash
docker compose up -d db              # Start PostgreSQL
uv run alembic upgrade head          # Run migrations
uv run alembic revision --autogenerate -m "message"  # Create migration
```

## Key Files

- `api/config.py` - Settings from environment variables
- `api/db/database.py` - Async SQLAlchemy engine and session
- `api/db/models.py` - SQLAlchemy ORM models
- `api/models/*.py` - Pydantic schemas
- `alembic/` - Database migrations
