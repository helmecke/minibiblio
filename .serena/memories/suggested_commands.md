# Development Commands

## Primary Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Run both Next.js and FastAPI development servers |
| `npm run next-dev` | Run only the Next.js development server |
| `npm run fastapi-dev` | Run only the FastAPI development server |
| `npm run build` | Build Next.js for production |
| `npm run start` | Start the production Next.js server |
| `npm run lint` | Run ESLint to check for code issues |

## Setup Commands

```bash
# Install Node.js dependencies
npm install

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync Python dependencies (optional - npm run dev does this automatically)
uv sync
```

## Python (uv) Commands

| Command | Description |
|---------|-------------|
| `uv sync` | Sync Python dependencies from pyproject.toml |
| `uv add <package>` | Add a new Python dependency |
| `uv remove <package>` | Remove a Python dependency |
| `uv run <command>` | Run a command in the virtual environment |

## URLs

| Service | URL |
|---------|-----|
| Next.js App | http://localhost:3000 |
| FastAPI Server | http://127.0.0.1:8000 |
| FastAPI Docs (via Next.js) | http://localhost:3000/api/python/docs |
| FastAPI Docs (direct) | http://127.0.0.1:8000/api/python/docs |
| Next.js API | http://localhost:3000/api/ |
| FastAPI via Next.js | http://localhost:3000/api/python/ |

## System Utilities (Linux)

- `git` - Version control
- `ls`, `cd`, `pwd` - Directory navigation
- `grep`, `find` - File searching
- `cat`, `less` - File viewing
