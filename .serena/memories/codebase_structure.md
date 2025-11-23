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
│   │   │   └── circulation/    # Loan management
│   │   │       ├── page.tsx    # Loans list
│   │   │       ├── loans-table.tsx
│   │   │       ├── checkout-dialog.tsx
│   │   │       └── [id]/       # Loan details
│   │   └── login/              # Login page
│   ├── globals.css             # Global styles
│   └── layout.tsx              # Root layout
│
├── api/                        # FastAPI Python backend
│   ├── index.py                # Main FastAPI app
│   ├── config.py               # Settings (pydantic-settings)
│   ├── db/                     # Database layer
│   │   ├── database.py         # Async SQLAlchemy engine
│   │   └── models.py           # ORM models (PatronDB, CatalogItemDB, LoanDB)
│   ├── models/                 # Pydantic schemas
│   │   ├── patron.py
│   │   ├── catalog.py
│   │   └── loan.py
│   └── routers/                # API routes
│       ├── patrons.py
│       ├── catalog.py
│       └── loans.py
│
├── alembic/                    # Database migrations
│   ├── env.py                  # Migration config
│   └── versions/               # Migration files
│
├── components/ui/              # Shadcn UI components
├── lib/                        # Utilities (auth, utils)
├── i18n/                       # Internationalization config
│   ├── config.ts               # Locale config (locales, defaultLocale)
│   ├── request.ts              # Server-side i18n setup
│   └── navigation.ts           # Localized Link, useRouter, etc.
├── messages/                   # Translation files
│   ├── en.json                 # English translations
│   └── de.json                 # German translations
├── middleware.ts               # Combined auth + i18n middleware
│
├── package.json                # Node.js dependencies
├── pyproject.toml              # Python dependencies
├── docker-compose.yml          # PostgreSQL database
├── next.config.js              # Next.js config (API rewrites)
├── CLAUDE.md                   # Claude Code guidance
└── README.md                   # Documentation
```

## Key Entry Points

- **Dashboard**: `app/[locale]/admin/page.tsx` - Main admin dashboard with stats
- **FastAPI**: `api/index.py` - Python API (routes at `/api/python/`)
- **Database**: `api/db/models.py` - SQLAlchemy models
- **Migrations**: `alembic/versions/` - Database migrations
- **i18n Config**: `i18n/config.ts` - Locale configuration
- **Translations**: `messages/en.json`, `messages/de.json`
