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
- **Local Authentication**: Username/password authentication system (NEW)
- **Docker Deployment**: Complete Windows deployment with Docker (NEW)

## Tech Stack

### Frontend
- **Next.js 14** (App Router) - React framework with server components
- **React 18** - UI library
- **TypeScript 5** - Type-safe JavaScript
- **Tailwind CSS 3** - Utility-first CSS framework
- **Shadcn UI** - Component library (Radix UI + Tailwind)
- **next-intl** - Internationalization (English + German)
- **NextAuth.js v5** - Authentication with Credentials provider (UPDATED)

### Backend
- **FastAPI** - Python web framework (accessible at `/api/python/`)
- **Next.js API Routes** - Server-side API endpoints (at `/api/`)
- **NextAuth.js v5** - Authentication with Google OAuth (optional)
- **PostgreSQL 17** - Database (via Docker)
- **SQLAlchemy 2.0** - ORM with async support (asyncpg driver)
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation and settings
- **JWT Authentication** - Token-based authentication (NEW)
- **Passlib** - Password hashing with bcrypt (NEW)

### Development Tools
- **ESLint** - JavaScript/TypeScript linting
- **uv** - Fast Python package manager
- **concurrently** - Run multiple dev servers
- **Docker Compose** - Database and services
- **Docker** - Production deployment (NEW)

## Architecture

- Admin dashboard at `/[locale]/admin` (protected by authentication)
- Login page at `/[locale]/login` with username/password form (UPDATED)
- FastAPI server mapped to `/api/python/` via Next.js rewrites
- Next.js API routes at `/api/`
- Python dependencies managed via `pyproject.toml` and `uv.lock`
- Locale-based routing with `[locale]` dynamic segment (en, de)
- Docker-based deployment with three services: nextjs, fastapi, db (NEW)

## Authentication System (NEW)

### Local Authentication
- **Username/Password**: Primary authentication method
- **JWT Tokens**: Secure session management
- **User Roles**: admin, librarian, user
- **Password Hashing**: bcrypt with passlib
- **Session Management**: NextAuth.js with Credentials provider

### User Management
- **UserDB Model**: Stores user credentials and roles
- **Admin Creation**: Automatic admin user creation on first startup
- **Role-based Access**: Different permissions for different roles
- **Password Change**: Secure password update functionality

### API Endpoints
- `POST /api/python/auth/login` - User login
- `GET /api/python/auth/me` - Get current user
- `POST /api/python/auth/change-password` - Update password
- `POST /api/python/auth/register` - Create first user

## Internationalization (i18n)

### Setup
- **Library**: next-intl
- **Supported Locales**: English (en), German (de)
- **Default Locale**: English
- **Locale Prefix**: Always (URLs include locale, e.g., `/en/admin`, `/de/admin`)

### Key Files
- `i18n/config.ts` - Locale configuration and types
- `i18n/request.ts` - Server-side i18n setup (getRequestConfig)
- `i18n/navigation.ts` - Localized navigation helpers (Link, useRouter, etc.)
- `middleware.ts` - Combined auth + i18n middleware
- `messages/en.json` - English translations (UPDATED)
- `messages/de.json` - German translations (UPDATED)

### Translation Namespaces
- `common` - Shared UI strings (save, cancel, delete, etc.)
- `nav` - Navigation labels
- `auth` - Authentication strings
- `dashboard` - Dashboard page
- `patrons` - Patron management
- `catalog` - Catalog management
- `circulation` - Loan management
- `import` - CSV import feature
- `settings` - Application settings
- `reports` - Reports and statistics (patronHistory, yearlyStats, bookHistory, table, status, months)
- `errors` - Error messages
- `login` - Login page (UPDATED with new authentication strings)

## Database

- PostgreSQL 17 running in Docker (port 5432)
- Test database on port 5433
- Async SQLAlchemy with asyncpg driver
- Alembic for migrations (async-compatible)
- Settings via pydantic-settings from `.env` file
- **Users Table**: New table for authentication (NEW)

### Database Commands
```bash
docker compose up -d db              # Start PostgreSQL
uv run alembic upgrade head          # Run migrations
uv run alembic revision --autogenerate -m "message"  # Create migration
```

### Database Models
- **UserDB**: User authentication and roles (NEW)
- **PatronDB**: Library members
- **CatalogItemDB**: Library items (books, DVDs, etc.)
- **LoanDB**: Loan records
- **AppSettingDB**: Application settings

## Docker Deployment (NEW)

### Services
- **nextjs**: Frontend application (port 3000)
- **fastapi**: Backend API (port 8000)
- **db**: PostgreSQL database (port 5432)

### Configuration Files
- `docker-compose.prod.yml` - Production Docker Compose
- `Dockerfile.nextjs` - Next.js production container
- `Dockerfile.fastapi` - FastAPI production container
- `docker-entrypoint.sh` - FastAPI startup script
- `.env.production` - Environment configuration template

### Windows Scripts
- `install.bat` - Installation and setup
- `start.bat` - Start all services
- `stop.bat` - Stop all services
- `logs.bat` - View application logs
- `update.bat` - Update to latest version
- `scripts/backup.bat` - Database backup
- `scripts/restore.bat` - Database restore
- `scripts/setup-auto-backup.bat` - Schedule automatic backups

## Implemented Features

### Patron Management
- **List**: `/admin/patrons` - Table with action menu (details, edit, delete)
- **Create**: Dialog modal via "Add Patron" button
- **Details**: `/admin/patrons/[id]` - View patron information
- **Edit**: `/admin/patrons/[id]/edit` - Update patron form
- **Delete**: Via action menu with confirmation

### Catalog Management
- **List**: `/admin/catalog` - Table with search, type/status filters
  - **Title Links**: Titles link to detail view
  - **Author Links**: Authors link to author page showing all items by that author
  - **Author Filtering**: URL parameter-based filtering by author name
- **Create**: Dialog modal via "Add Item" button
- **Details**: `/admin/catalog/[id]` - View item information
- **Edit**: `/admin/catalog/[id]/edit` - Update item form
- **Delete**: Via action menu with confirmation
- **Types**: book, dvd, cd, magazine, other
- **Statuses**: available, borrowed, reserved, damaged, lost

### Circulation (Loans)
- **List**: `/admin/circulation` - All loans with status indicators
- **Checkout**: Dialog to check out item to patron (sets item status to borrowed)
- **Return**: Action to return item (sets item status to available)
- **Extend**: Action to extend due date (uses configurable extension period from settings)
- **Details**: `/admin/circulation/[id]` - View loan with linked item/patron
- **Overdue**: Visual indicators for overdue items
- **Dashboard**: Shows active loans and overdue counts
- **Configurable Periods**: All loan periods (default, available options, extension) are configurable in Settings

### CSV Import
- **Page**: `/admin/import` - Import catalog items from CSV files
- **Preview**: Upload CSV → validate rows → show preview with status
- **Column Detection**: Auto-detects Titel, Autor/Verlag, Genres, InventarNr., ISBN
- **Validation**: Checks required fields, ISBN format
- **Duplicate Handling**: Skip, update existing, or always create new
- **Encoding Support**: UTF-8-sig and latin-1 fallback for German characters

### Settings
- **Page**: `/admin/settings` - Application configuration
- **Catalog ID Format**: Configurable format (default: `{number}/{year}` → "1/24", "2/24")
- **Counter Management**: Auto-increment, resets to 1 on new year
- **Loan Periods**: Configurable default loan period, available periods, and extension period
  - Default Period: Number of days for default checkout (default: 14)
  - Available Periods: Comma-separated list of selectable periods (default: 7, 14, 21, 28)
  - Extension Period: Number of days to extend when renewing (default: 7)
- **Database**: Settings stored in `app_settings` table (key-value JSON)

### Reports
- **Page**: `/admin/reports` - Library statistics and loan history
- **Patron Loan History (Leserverzeichnis)**: Select patron → view all loans with dates, status
- **Yearly Statistics (Jahresstatistik)**: Select year → total loans, unique books/patrons, monthly breakdown, top 10 books
- **Patron Detail Integration**: Loan history table shown on `/admin/patrons/[id]`
- **Catalog Detail Integration**: Loan history table shown on `/admin/catalog/[id]`

### Quick Actions
- **Checkout from Catalog**: Available items show "Checkout" button on detail page and in table "..." menu
- **Checkout Dialog**: Pre-selects item, user picks patron + loan period

### Authentication (NEW)
- **Login Page**: Username/password form with error handling
- **Session Management**: JWT-based secure sessions
- **User Roles**: Admin, librarian, user with different permissions
- **Password Security**: Bcrypt hashing, secure password change
- **Default Admin**: Automatic admin user creation on first startup

## Database Models

### UserDB (NEW)
- `id` (UUID, primary key)
- `username` (unique, required)
- `email` (unique, optional)
- `hashed_password` (bcrypt hash, required)
- `is_active` (boolean, default: true)
- `role` (enum: admin/librarian/user, default: user)
- `created_at`, `updated_at` (timestamps)

### PatronDB
- `id` (UUID, primary key)
- `membership_id` (auto: "LIB-XXXXXXXX")
- `first_name`, `last_name` (required)
- `email`, `phone` (optional)
- `address` (optional, Text field for multi-line addresses)
- `birthdate` (optional, Date field)
- `status` (active/inactive/suspended)
- `created_at`, `updated_at`

### CatalogItemDB
- `id` (UUID, primary key)
- `catalog_id` (auto: "CAT-XXXXXXXX")
- `type` (book/dvd/cd/magazine/other)
- `title` (required), `author`, `isbn`, `publisher`, `year`
- `description`, `genre`, `language`, `location`
- `status` (available/borrowed/reserved/damaged/lost)
- `created_at`, `updated_at`

### LoanDB
- `id` (UUID, primary key)
- `loan_id` (auto: "LN-XXXXXXXX")
- `catalog_item_id`, `patron_id` (foreign keys)
- `checkout_date`, `due_date`, `return_date`
- `status` (active/returned/overdue/lost)
- `notes`, `created_at`, `updated_at`

## API Endpoints

### Authentication (NEW)
- `POST /api/python/auth/login` - User login with username/password
- `GET /api/python/auth/me` - Get current user information
- `POST /api/python/auth/change-password` - Change user password
- `POST /api/python/auth/register` - Create first user (if no users exist)

### Patrons (`/api/python/patrons`)
- GET `/` - List patrons (filter by status)
- GET `/count` - Count patrons
- GET `/{id}` - Get patron details
- POST `/` - Create patron
- PUT `/{id}` - Update patron
- DELETE `/{id}` - Delete patron

### Catalog (`/api/python/catalog`)
- GET `/` - List items (filter by type, status, search)
- GET `/count` - Count items
- GET `/{id}` - Get item details
- POST `/` - Create item
- PUT `/{id}` - Update item
- DELETE `/{id}` - Delete item

### Loans (`/api/python/loans`)
- GET `/` - List loans (filter by status, patron, item)
- GET `/count` - Count loans
- GET `/active/count` - Count active loans
- GET `/overdue` - List overdue loans
- GET `/{id}` - Get loan details
- POST `/checkout` - Check out item to patron
- POST `/{id}/return` - Return item
- POST `/{id}/extend` - Extend due date

### Import (`/api/python/import`)
- POST `/catalog/preview` - Preview CSV file (multipart/form-data)
- POST `/catalog` - Import catalog items from CSV (multipart/form-data, query params: duplicate_handling, default_language)

### Settings (`/api/python/settings`)
- GET `/catalog-id/config` - Get catalog ID configuration
- PUT `/catalog-id/config` - Update catalog ID configuration
- GET `/catalog-id/preview` - Preview next catalog ID
- GET `/loan-periods/config` - Get loan period settings (default_period, available_periods, extension_period)
- PUT `/loan-periods/config` - Update loan period settings

### Reports (`/api/python/reports`)
- GET `/patrons` - List patrons for report dropdown
- GET `/patron/{patron_id}/loans` - Get complete loan history for a patron
- GET `/book/{item_id}/loans` - Get complete loan history for a book
- GET `/statistics/yearly?year=YYYY` - Get yearly statistics (total loans, unique books/patrons, top 10, monthly breakdown)

## Key Files

### Backend
- `api/config.py` - Settings from environment (UPDATED with JWT settings)
- `api/db/database.py` - Async SQLAlchemy engine
- `api/db/models.py` - ORM models (PatronDB, CatalogItemDB, LoanDB, UserDB - NEW)
- `api/models/` - Pydantic schemas (patron.py, catalog.py, loan.py, import_models.py, reports.py, settings.py, user.py - NEW)
- `api/routers/` - API routes (patrons.py, catalog.py, loans.py, import_router.py, reports.py, settings.py, auth.py - NEW)
- `api/scripts/create_admin.py` - Admin user creation script (NEW)
- `alembic/versions/` - Database migrations (f1a2b3c4d5e6_add_users_table.py - NEW)

### Frontend
- `app/[locale]/admin/page.tsx` - Dashboard with stats
- `app/[locale]/admin/layout.tsx` - Admin layout with sidebar
- `app/[locale]/admin/nav-item.tsx` - Sidebar nav component
- `app/[locale]/admin/user.tsx` - User menu component
- `app/[locale]/admin/providers.tsx` - Client providers
- `app/[locale]/admin/language-switcher.tsx` - EN/DE toggle
- `app/[locale]/admin/patrons/` - Patron management pages
- `app/[locale]/admin/catalog/` - Catalog management pages
- `app/[locale]/admin/circulation/` - Loan management pages
- `app/[locale]/admin/import/` - CSV import page
- `app/[locale]/admin/settings/` - Settings page
- `app/[locale]/admin/reports/` - Reports page (patron history, yearly stats)
- `app/[locale]/login/page.tsx` - Login page with username/password form (UPDATED)
- `i18n/` - Internationalization config (config.ts, request.ts, navigation.ts)
- `messages/` - Translation files (en.json, de.json - UPDATED with login strings)
- `lib/auth.ts` - NextAuth configuration with Credentials provider (UPDATED)

### Docker & Deployment (NEW)
- `docker-compose.prod.yml` - Production Docker Compose
- `Dockerfile.nextjs` - Next.js production container
- `Dockerfile.fastapi` - FastAPI production container
- `docker-entrypoint.sh` - FastAPI startup script
- `.env.production` - Environment configuration template
- `install.bat` - Windows installation script
- `start.bat` - Windows startup script
- `stop.bat` - Windows stop script
- `logs.bat` - Windows logs script
- `update.bat` - Windows update script
- `scripts/backup.bat` - Database backup script
- `scripts/restore.bat` - Database restore script
- `scripts/setup-auto-backup.bat` - Automatic backup setup
- `DEPLOYMENT.md` - Complete deployment documentation

### Shadcn UI Components
Located in `components/ui/`: button, badge, card, dialog, dropdown-menu, input, label, select, sheet, table, textarea, tooltip

## Deployment (NEW)

### Windows 11 Docker Deployment
- **One-click installation**: `install.bat` script
- **Automatic setup**: Docker image building, database initialization
- **Secure defaults**: Admin user creation, password requirements
- **Easy management**: Start/stop/logs/update scripts
- **Data persistence**: Docker volumes for database storage
- **Backup system**: Manual and automatic database backups
- **Production ready**: Health checks, restart policies, logging

### Security Features
- **Local authentication**: No external dependencies required
- **Secure passwords**: Bcrypt hashing, minimum requirements
- **JWT tokens**: Secure session management
- **Environment variables**: Sensitive data not in code
- **Docker isolation**: Containerized services
- **Backup encryption**: Optional backup encryption

### Maintenance
- **Automatic updates**: `update.bat` script
- **Health monitoring**: Docker health checks
- **Log management**: Centralized logging with `logs.bat`
- **Backup scheduling**: Windows Task Scheduler integration
- **Resource monitoring**: Docker Desktop resource usage

## Development vs Production

### Development
- Uses `docker-compose.yml` (development services)
- Hot reload enabled
- Debug logging
- Local database on port 5432
- Next.js dev server on port 3000
- FastAPI dev server on port 8000

### Production (NEW)
- Uses `docker-compose.prod.yml` (production services)
- Optimized Docker images
- Health checks enabled
- Restart policies configured
- Standalone Next.js build
- Production logging
- Secure defaults

## Migration Path

### From Development to Production
1. **Backup development data**: `scripts/backup.bat`
2. **Configure production**: Edit `.env` file
3. **Run production install**: `install.bat`
4. **Restore data**: `scripts/restore.bat`
5. **Test functionality**: Verify all features work

### Data Portability
- **SQL dumps**: Standard PostgreSQL format
- **Cross-platform**: Works on any system with Docker
- **Version control**: Database schema tracked with Alembic
- **Backup automation**: Scheduled backups with timestamps