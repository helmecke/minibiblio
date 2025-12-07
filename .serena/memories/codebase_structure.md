# Codebase Structure

```
minibiblio/
├── app/                        # Next.js App Router directory
│   ├── api/                    # Next.js API routes
│   │   └── healthcheck/        # Healthcheck endpoint
│   ├── [locale]/               # Locale-based routing (en, de)
│   │   ├── layout.tsx          # Locale layout with NextIntlClientProvider
│   │   ├── page.tsx            # Home page
│   │   ├── admin/              # Admin dashboard (protected)
│   │   │   ├── layout.tsx      # Admin layout with sidebar
│   │   │   ├── page.tsx        # Dashboard with stats
│   │   │   ├── nav-item.tsx    # Sidebar nav component
│   │   │   ├── user.tsx        # User menu component
│   │   │   ├── providers.tsx   # Client providers
│   │   │   ├── language-switcher.tsx  # EN/DE toggle
│   │   │   ├── patrons/        # Patron management
│   │   │   │   ├── page.tsx    # Patrons list
│   │   │   │   ├── patrons-table.tsx
│   │   │   │   ├── add-patron-dialog.tsx
│   │   │   │   └── [id]/       # Patron details/edit
│   │   │   ├── catalog/        # Catalog management
│   │   │   │   ├── page.tsx    # Catalog list
│   │   │   │   ├── catalog-table.tsx
│   │   │   │   ├── add-catalog-dialog.tsx
│   │   │   │   └── [id]/       # Item details/edit
│   │   │   ├── circulation/    # Loan management
│   │   │   │   ├── page.tsx    # Loans list
│   │   │   │   ├── loans-table.tsx
│   │   │   │   ├── checkout-dialog.tsx
│   │   │   │   └── [id]/       # Loan details
│   │   │   ├── import/         # CSV import
│   │   │   │   └── page.tsx    # Import page with upload/preview/import
│   │   │   └── settings/       # Application settings
│   │   │       └── page.tsx    # Settings page with catalog ID config
│   │   └── login/              # Login page (UPDATED)
│   │       └── page.tsx        # Username/password login form
│   ├── globals.css             # Global styles
│   └── layout.tsx              # Root layout
│
├── api/                        # FastAPI Python backend
│   ├── index.py                # Main FastAPI app (UPDATED with auth router)
│   ├── config.py               # Settings (pydantic-settings) (UPDATED with JWT)
│   ├── db/                     # Database layer
│   │   ├── database.py         # Async SQLAlchemy engine (UPDATED)
│   │   └── models.py           # ORM models (UPDATED with UserDB)
│   ├── models/                 # Pydantic schemas
│   │   ├── patron.py
│   │   ├── catalog.py
│   │   ├── loan.py
│   │   ├── import_models.py    # Import/export schemas
│   │   ├── reports.py
│   │   ├── settings.py
│   │   └── user.py             # User authentication schemas (NEW)
│   ├── routers/                # API routes
│   │   ├── auth.py             # Authentication endpoints (NEW)
│   │   ├── patrons.py
│   │   ├── catalog.py
│   │   ├── loans.py
│   │   ├── import_router.py    # CSV import endpoints
│   │   ├── settings.py         # App settings & catalog ID config
│   │   └── reports.py
│   └── scripts/                # Utility scripts
│       └── create_admin.py    # Admin user creation (NEW)
│
├── alembic/                    # Database migrations
│   ├── env.py                  # Migration config
│   └── versions/               # Migration files
│       └── f1a2b3c4d5e6_add_users_table.py  # Users table migration (NEW)
│
├── components/ui/              # Shadcn UI components
├── lib/                        # Utilities (auth, utils)
│   └── auth.ts                 # NextAuth configuration (UPDATED)
├── i18n/                       # Internationalization config
│   ├── config.ts               # Locale config (locales, defaultLocale)
│   ├── request.ts              # Server-side i18n setup
│   └── navigation.ts           # Localized Link, useRouter, etc.
├── messages/                   # Translation files
│   ├── en.json                 # English translations (UPDATED)
│   └── de.json                 # German translations (UPDATED)
├── middleware.ts               # Combined auth + i18n middleware
├── scripts/                    # Windows batch scripts (NEW)
│   ├── backup.bat              # Database backup
│   ├── restore.bat             # Database restore
│   └── setup-auto-backup.bat   # Schedule automatic backups
│
├── package.json                # Node.js dependencies
├── pyproject.toml              # Python dependencies (UPDATED with auth)
├── docker-compose.yml          # PostgreSQL database (development)
├── docker-compose.prod.yml     # Production Docker Compose (NEW)
├── next.config.js              # Next.js config (UPDATED for standalone)
├── CLAUDE.md                   # Claude Code guidance
├── DEPLOYMENT.md               # Deployment documentation (NEW)
├── Dockerfile.nextjs           # Next.js production container (NEW)
├── Dockerfile.fastapi          # FastAPI production container (NEW)
├── docker-entrypoint.sh        # FastAPI startup script (NEW)
├── .env.production             # Environment template (NEW)
├── install.bat                 # Windows installation script (NEW)
├── start.bat                   # Windows startup script (NEW)
├── stop.bat                    # Windows stop script (NEW)
├── logs.bat                    # Windows logs script (NEW)
├── update.bat                  # Windows update script (NEW)
├── README.md                   # Documentation
└── backups/                    # Database backups (auto-created) (NEW)
```

## Key Entry Points

- **Dashboard**: `app/[locale]/admin/page.tsx` - Main admin dashboard with stats
- **FastAPI**: `api/index.py` - Python API (routes at `/api/python/`)
- **Database**: `api/db/models.py` - SQLAlchemy models (UPDATED with UserDB)
- **Migrations**: `alembic/versions/` - Database migrations (NEW users table)
- **i18n Config**: `i18n/config.ts` - Locale configuration
- **Translations**: `messages/en.json`, `messages/de.json` (UPDATED)
- **Authentication**: `lib/auth.ts` - NextAuth with Credentials provider (UPDATED)
- **Login Page**: `app/[locale]/login/page.tsx` - Username/password form (UPDATED)
- **Docker Production**: `docker-compose.prod.yml` - Production deployment (NEW)
- **Windows Scripts**: `*.bat` files - One-click management (NEW)

## New Files for Windows Deployment (15 total)

### Docker Configuration
- `Dockerfile.nextjs` - Next.js production container
- `Dockerfile.fastapi` - FastAPI production container  
- `docker-compose.prod.yml` - Production Docker Compose
- `docker-entrypoint.sh` - FastAPI startup script

### Environment & Configuration
- `.env.production` - Environment configuration template
- `DEPLOYMENT.md` - Complete deployment documentation

### Windows Management Scripts
- `install.bat` - Installation and setup
- `start.bat` - Start all services
- `stop.bat` - Stop all services
- `logs.bat` - View application logs
- `update.bat` - Update to latest version

### Backup & Restore
- `scripts/backup.bat` - Database backup
- `scripts/restore.bat` - Database restore
- `scripts/setup-auto-backup.bat` - Schedule automatic backups

### Authentication Backend
- `api/models/user.py` - User authentication schemas
- `api/routers/auth.py` - Authentication endpoints
- `api/scripts/create_admin.py` - Admin user creation script
- `alembic/versions/f1a2b3c4d5e6_add_users_table.py` - Users table migration

## Modified Files (8 total)

### Backend Updates
- `pyproject.toml` - Added authentication dependencies (passlib, python-jose)
- `api/config.py` - Added JWT configuration settings
- `api/db/models.py` - Added UserDB model and UserRole enum
- `api/db/database.py` - Added get_async_session alias
- `api/index.py` - Registered auth router

### Frontend Updates
- `lib/auth.ts` - Added Credentials provider to NextAuth
- `app/[locale]/login/page.tsx` - Updated with username/password form
- `next.config.js` - Added standalone output for Docker
- `messages/en.json` - Added login form translations
- `messages/de.json` - Added login form translations

## Authentication Flow

### Frontend (Next.js)
1. User enters username/password on login page
2. NextAuth Credentials provider calls FastAPI login endpoint
3. FastAPI validates credentials and returns JWT token
4. NextAuth creates session with JWT token
5. User is redirected to admin dashboard

### Backend (FastAPI)
1. Login endpoint validates username/password
2. JWT token is generated with user information
3. Token is returned to frontend
4. Subsequent API calls include JWT token
5. Token is validated on protected endpoints

### Database
1. User credentials stored in `users` table
2. Passwords hashed with bcrypt
3. User roles determine permissions
4. Admin user created automatically on first startup

## Docker Architecture

### Services
- **nextjs**: Frontend application (port 3000)
  - Standalone Next.js build
  - Environment variables for authentication
  - Health checks and restart policies

- **fastapi**: Backend API (port 8000)
  - Python with uv package manager
  - Automatic database migrations
  - Admin user creation on startup
  - Health checks and restart policies

- **db**: PostgreSQL database (port 5432)
  - Official PostgreSQL 17 image
  - Persistent data volume
  - Backup directory mount
  - Health checks and restart policies

### Networking
- Services communicate via Docker network
- Next.js proxies `/api/python/*` to FastAPI
- FastAPI connects to PostgreSQL via service name
- External access only through Next.js (port 3000)

### Data Persistence
- PostgreSQL data stored in Docker volume
- Backups stored in mounted directory
- Configuration via environment variables
- Survives container restarts and updates

## Security Implementation

### Authentication
- **Password Hashing**: bcrypt with passlib
- **JWT Tokens**: Secure session management
- **Token Expiration**: 60 minutes (configurable)
- **Password Requirements**: Minimum 8 characters

### Environment Security
- **Secrets**: JWT_SECRET, AUTH_SECRET generated randomly
- **Database Password**: Strong password required
- **No Hardcoded Secrets**: All sensitive data in environment variables
- **Production Defaults**: Secure defaults for production

### Docker Security
- **Container Isolation**: Services isolated in containers
- **Non-root Users**: Containers run as non-root users
- **Health Checks**: Service health monitoring
- **Restart Policies**: Automatic recovery from failures

## Development vs Production Differences

### Development
- Uses `docker-compose.yml` (development services)
- Hot reload enabled for both frontend and backend
- Debug logging and error details
- Local database on port 5432
- Next.js dev server on port 3000
- FastAPI dev server on port 8000
- Google OAuth enabled by default

### Production
- Uses `docker-compose.prod.yml` (production services)
- Optimized Docker images with multi-stage builds
- Health checks enabled for all services
- Restart policies configured for reliability
- Standalone Next.js build for production
- Production logging with structured output
- Local authentication by default (Google OAuth optional)
- Secure defaults and environment validation

## Migration and Updates

### Database Migrations
- Alembic tracks all schema changes
- Automatic migration on container startup
- Version control for database schema
- Rollback capability if needed

### Application Updates
- `update.bat` script handles updates
- Docker images rebuilt with latest code
- Database migrations applied automatically
- Services restarted with new versions
- Data preserved during updates

### Configuration Updates
- Environment variables in `.env` file
- Template provided in `.env.production`
- Validation of required settings
- Secure defaults for production
- Documentation for all configuration options