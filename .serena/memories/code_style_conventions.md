# Code Style and Conventions

## TypeScript/JavaScript

### Compiler Settings
- Target: ES5
- Strict mode: enabled
- JSX: preserve (for Next.js)
- Module resolution: Node

### Path Aliases
- `@/*` maps to project root (e.g., `import { foo } from '@/lib/utils'`)

### Component Style
- Use function components with default exports for pages
- React component files use `.tsx` extension
- Use `type` imports when importing only types: `import { type NextRequest }`

### ESLint
- Extends `next/core-web-vitals` configuration
- Run with `npm run lint`

## CSS/Styling
- Tailwind CSS utility classes
- Global styles in `app/globals.css`
- Use className for styling (no CSS modules or styled-components)

## Python (FastAPI)

### Style
- Standard Python conventions
- Type hints recommended
- Decorator-based route definitions (`@app.get`, `@app.post`, etc.)

### API Endpoints
- FastAPI endpoints should be prefixed with `/api/py/`
- Use descriptive function names for route handlers

## File Organization

```
app/              # Next.js App Router
  api/            # Next.js API routes
  page.tsx        # Page components
  layout.tsx      # Layout components
  globals.css     # Global styles
api/              # FastAPI Python backend
  index.py        # Main FastAPI application
public/           # Static assets
```
