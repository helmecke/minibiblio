# MiniBiblio - Project Overview

## Purpose
MiniBiblio is a hybrid Next.js + Python application that combines a fullstack Next.js frontend with a FastAPI Python backend. This architecture is well-suited for applications that need Python AI/ML libraries on the backend while maintaining a modern React-based frontend.

## Tech Stack

### Frontend
- **Next.js 13** (App Router) - React framework with server components
- **React 18** - UI library
- **TypeScript 5** - Type-safe JavaScript
- **Tailwind CSS 3** - Utility-first CSS framework
- **PostCSS** - CSS processing

### Backend
- **FastAPI** - Modern Python web framework (accessible at `/api/python/`)
- **Next.js API Routes** - Server-side API endpoints (at `/api/`)
- **Uvicorn** - ASGI server for FastAPI

### Development Tools
- **ESLint** - JavaScript/TypeScript linting
- **concurrently** - Run multiple commands simultaneously
- **uv** - Fast Python package manager (replaces pip/venv)

## Architecture

- FastAPI server is mapped to `/api/python/` via Next.js rewrites
- Next.js API routes are at `/api/`
- In development: FastAPI runs on port 8000, Next.js on port 3000
- Python dependencies managed via `pyproject.toml` and `uv.lock`
- Virtual environment at `.venv` (managed by uv)
