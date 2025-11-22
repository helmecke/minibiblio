# Codebase Structure

```
minibiblio/
├── app/                    # Next.js App Router directory
│   ├── api/                # Next.js API routes
│   │   └── healthcheck/    # Healthcheck endpoint
│   │       └── route.ts    # GET /api/healthcheck
│   ├── favicon.ico         # Site favicon
│   ├── globals.css         # Global Tailwind CSS styles
│   ├── layout.tsx          # Root layout component
│   └── page.tsx            # Home page component
│
├── api/                    # FastAPI Python backend
│   └── index.py            # Main FastAPI app (routes at /api/python/)
│
├── public/                 # Static assets served at /
│
├── .claude/                # Claude Code configuration
├── .serena/                # Serena configuration
├── .venv/                  # Python virtual environment (managed by uv)
│
├── package.json            # Node.js dependencies and scripts
├── pyproject.toml          # Python project config and dependencies
├── uv.lock                 # Python dependency lock file
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── postcss.config.js       # PostCSS configuration
├── next.config.js          # Next.js configuration (includes rewrites for /api/python/)
├── .eslintrc.json          # ESLint configuration
├── .gitignore              # Git ignore rules
├── LICENSE                 # Project license
├── CLAUDE.md               # Claude Code guidance
└── README.md               # Project documentation
```

## Key Entry Points

- **Frontend**: `app/page.tsx` - Main page component
- **Next.js API**: `app/api/*/route.ts` - API route handlers
- **FastAPI**: `api/index.py` - Python API application (routes prefixed with `/api/python/`)
