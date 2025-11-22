# MiniBiblio - Project Overview

## Purpose
MiniBiblio is a comprehensive library management system for small libraries.

## Features

- **Book Management**: Add, edit, delete, and search books
- **Patron Management**: Full CRUD for library members (implemented)
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

## Implemented Features

### Patron Management
- **List**: `/admin/patrons` - Table with action menu (details, edit, delete)
- **Create**: Dialog modal via "Add Patron" button
- **Details**: `/admin/patrons/[id]` - View patron information
- **Edit**: `/admin/patrons/[id]/edit` - Update patron form
- **Delete**: Via action menu with confirmation

### Patron Model
- `id` (UUID, auto-generated)
- `membership_id` (string, auto-generated like "LIB-XXXXXXXX")
- `first_name`, `last_name` (required)
- `email`, `phone` (optional)
- `status` (active/inactive/suspended)
- `created_at`, `updated_at` (timestamps)

## Key Files

### Backend
- `api/config.py` - Settings from environment variables
- `api/db/database.py` - Async SQLAlchemy engine and session
- `api/db/models.py` - SQLAlchemy ORM models (PatronDB)
- `api/models/patron.py` - Pydantic schemas
- `api/routers/patrons.py` - CRUD endpoints
- `alembic/` - Database migrations

### Frontend (Patrons)
- `app/admin/patrons/page.tsx` - List page
- `app/admin/patrons/patrons-table.tsx` - Table with actions
- `app/admin/patrons/add-patron-dialog.tsx` - Create dialog
- `app/admin/patrons/[id]/page.tsx` - Details page
- `app/admin/patrons/[id]/edit/page.tsx` - Edit page
- `app/admin/patrons/[id]/edit/edit-patron-form.tsx` - Edit form

### Shadcn UI Components
Located in `components/ui/`: button, badge, card, dialog, dropdown-menu, input, label, select, sheet, table, tooltip
