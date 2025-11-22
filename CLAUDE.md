# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

```bash
npm run dev          # Run both Next.js and FastAPI servers concurrently
npm run next-dev     # Run only Next.js (port 3000)
npm run fastapi-dev  # Run only FastAPI (port 8000)
npm run build        # Production build
npm run lint         # Run ESLint

# Python (uv)
uv sync              # Sync Python dependencies
uv add <package>     # Add Python dependency
uv run <command>     # Run command in venv
```

## Architecture

This is a hybrid Next.js + FastAPI application with two API backends:

- **Next.js API routes** (`/api/*`) - TypeScript handlers in `app/api/`
- **FastAPI Python backend** (`/api/python/*`) - Python handlers in `api/index.py`

The FastAPI server is proxied through Next.js via rewrites in `next.config.js`. In development, requests to `/api/python/*` are forwarded to `http://127.0.0.1:8000`. FastAPI docs are available at `/api/python/docs` or `/docs`.

## Key Paths

- `app/` - Next.js App Router (pages, layouts, API routes)
- `api/` - FastAPI Python backend
- `pyproject.toml` - Python dependencies (managed by uv)
- `@/*` - TypeScript path alias for project root imports

# Context7 MCP Server

**Purpose**: Official library documentation lookup and framework pattern guidance

## Triggers

- Import statements: `import`, `require`, `from`, `use`
- Framework keywords: React, Vue, Angular, Next.js, Express, etc.
- Library-specific questions about APIs or best practices
- Need for official documentation patterns vs generic solutions
- Version-specific implementation requirements

## Choose When

- **Over WebSearch**: When you need curated, version-specific documentation
- **Over native knowledge**: When implementation must follow official patterns
- **For frameworks**: React hooks, Vue composition API, Angular services
- **For libraries**: Correct API usage, authentication flows, configuration
- **For compliance**: When adherence to official standards is mandatory

## Works Best With

- **Sequential**: Context7 provides docs → Sequential analyzes implementation strategy
- **Magic**: Context7 supplies patterns → Magic generates framework-compliant components

## Examples

```
"implement React useEffect" → Context7 (official React patterns)
"add authentication with Auth0" → Context7 (official Auth0 docs)
"migrate to Vue 3" → Context7 (official migration guide)
"optimize Next.js performance" → Context7 (official optimization patterns)
"just explain this function" → Native Claude (no external docs needed)
```

# Sequential MCP Server

**Purpose**: Multi-step reasoning engine for complex analysis and systematic problem solving

## Triggers

- Complex debugging scenarios with multiple layers
- Architectural analysis and system design questions
- `--think`, `--think-hard`, `--ultrathink` flags
- Problems requiring hypothesis testing and validation
- Multi-component failure investigation
- Performance bottleneck identification requiring methodical approach

## Choose When

- **Over native reasoning**: When problems have 3+ interconnected components
- **For systematic analysis**: Root cause analysis, architecture review, security assessment
- **When structure matters**: Problems benefit from decomposition and evidence gathering
- **For cross-domain issues**: Problems spanning frontend, backend, database, infrastructure
- **Not for simple tasks**: Basic explanations, single-file changes, straightforward fixes

## Works Best With

- **Context7**: Sequential coordinates analysis → Context7 provides official patterns
- **Magic**: Sequential analyzes UI logic → Magic implements structured components
- **Playwright**: Sequential identifies testing strategy → Playwright executes validation

## Examples

```
"why is this API slow?" → Sequential (systematic performance analysis)
"design a microservices architecture" → Sequential (structured system design)
"debug this authentication flow" → Sequential (multi-component investigation)
"analyze security vulnerabilities" → Sequential (comprehensive threat modeling)
"explain this function" → Native Claude (simple explanation)
"fix this typo" → Native Claude (straightforward change)
```

# Serena MCP Server

**Purpose**: Semantic code understanding with project memory and session persistence

## Triggers

- Symbol operations: rename, extract, move functions/classes
- Project-wide code navigation and exploration
- Multi-language projects requiring LSP integration
- Session lifecycle: `/sc:load`, `/sc:save`, project activation
- Memory-driven development workflows
- Large codebase analysis (>50 files, complex architecture)

## Choose When

- **Over Morphllm**: For symbol operations, not pattern-based edits
- **For semantic understanding**: Symbol references, dependency tracking, LSP integration
- **For session persistence**: Project context, memory management, cross-session learning
- **For large projects**: Multi-language codebases requiring architectural understanding
- **Not for simple edits**: Basic text replacements, style enforcement, bulk operations

## Works Best With

- **Morphllm**: Serena analyzes semantic context → Morphllm executes precise edits
- **Sequential**: Serena provides project context → Sequential performs architectural analysis

## Examples

```
"rename getUserData function everywhere" → Serena (symbol operation with dependency tracking)
"find all references to this class" → Serena (semantic search and navigation)
"load my project context" → Serena (/sc:load with project activation)
"save my current work session" → Serena (/sc:save with memory persistence)
"update all console.log to logger" → Morphllm (pattern-based replacement)
"create a login form" → Magic (UI component generation)
```

# GitHub MCP Server

**Purpose**: Direct GitHub platform integration for repository management, issues, PRs, CI/CD, and code analysis

## Triggers

- Repository operations: browse code, search files, analyze commits, manage branches
- Issue management: create, update, triage, comment on issues
- Pull request workflows: create PRs, review code, merge changes
- CI/CD operations: monitor GitHub Actions, analyze build failures, manage releases
- Code security: scanning alerts, Dependabot alerts, secret scanning
- Team collaboration: discussions, notifications, project boards

## Choose When

- **Over manual git commands**: For GitHub-specific operations (issues, PRs, Actions)
- **For automation**: Creating issues/PRs programmatically, bulk operations
- **For code review**: Adding review comments, approving/requesting changes
- **For CI/CD insight**: Checking workflow status, analyzing failed builds
- **For security**: Reviewing code scanning alerts, Dependabot updates

## Default Toolsets

- `context` - Current user and GitHub context
- `repos` - Repository operations (branches, commits, files)
- `issues` - Issue management
- `pull_requests` - PR operations
- `users` - User information

## Additional Toolsets

- `actions` - GitHub Actions workflows
- `code_security` - Code scanning alerts
- `dependabot` - Dependency alerts
- `discussions` - GitHub Discussions
- `projects` - GitHub Projects
- `notifications` - Notification management
- `secret_protection` - Secret scanning

## Works Best With

- **Serena**: GitHub provides remote context → Serena handles local semantic operations
- **Sequential**: GitHub surfaces issue/PR context → Sequential analyzes complex problems

## Examples

```
"create an issue for this bug" → GitHub (issue_write with method: create)
"list open PRs" → GitHub (list_pull_requests)
"check CI status" → GitHub (pull_request_read with method: get_status)
"review this PR" → GitHub (pull_request_review_write)
"search for authentication code" → GitHub (search_code)
"what failed in the build?" → GitHub (get_job_logs with failed_only: true)
```
