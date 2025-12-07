# Docker GitHub Packages Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Automate Docker image building and publishing to GitHub Container Registry (ghcr.io) triggered by semantic version tags on main branch.

**Architecture:** GitHub Actions workflow with matrix strategy builds Next.js and FastAPI images in parallel, tags with version + latest, pushes to ghcr.io. Docker Compose updated to pull pre-built images using .env version variable.

**Tech Stack:** GitHub Actions, Docker Buildx, GitHub Container Registry (ghcr.io), Docker Compose

---

## Task 1: Create GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/docker-publish.yml`

**Step 1: Create workflow file with trigger and permissions**

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Build and Publish Docker Images

on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        include:
          - image: nextjs
            dockerfile: Dockerfile.nextjs
            context: .
          - image: fastapi
            dockerfile: Dockerfile.fastapi
            context: .
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Extract version from tag
        id: version
        run: |
          # Strip 'v' prefix from tag (v1.0.0 -> 1.0.0)
          VERSION=${GITHUB_REF#refs/tags/v}
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Building version: $VERSION"
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.context }}
          file: ${{ matrix.dockerfile }}
          push: true
          tags: |
            ghcr.io/${{ github.repository_owner }}/minibiblio-${{ matrix.image }}:${{ steps.version.outputs.version }}
            ghcr.io/${{ github.repository_owner }}/minibiblio-${{ matrix.image }}:latest
          platforms: linux/amd64
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Step 2: Verify workflow syntax**

Run: `cat .github/workflows/docker-publish.yml`
Expected: File content displays correctly, valid YAML syntax

**Step 3: Commit workflow**

```bash
git add .github/workflows/docker-publish.yml
git commit -m "ci: add Docker image build and publish workflow"
```

---

## Task 2: Update Docker Compose for Pre-built Images

**Files:**
- Modify: `docker-compose.prod.yml`

**Step 1: Read current docker-compose.prod.yml**

Run: `cat docker-compose.prod.yml`
Expected: See current build configuration for fastapi and nextjs services

**Step 2: Replace build with image references**

Edit `docker-compose.prod.yml`, replace the fastapi service:

**Before:**
```yaml
  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    container_name: minibiblio-fastapi
```

**After:**
```yaml
  fastapi:
    image: ghcr.io/helmecke/minibiblio-fastapi:${MINIBIBLIO_VERSION:-latest}
    container_name: minibiblio-fastapi
```

Replace the nextjs service:

**Before:**
```yaml
  nextjs:
    build:
      context: .
      dockerfile: Dockerfile.nextjs
    container_name: minibiblio-nextjs
```

**After:**
```yaml
  nextjs:
    image: ghcr.io/helmecke/minibiblio-nextjs:${MINIBIBLIO_VERSION:-latest}
    container_name: minibiblio-nextjs
```

**Step 3: Verify changes**

Run: `grep -A2 "image: ghcr.io" docker-compose.prod.yml`
Expected: See both fastapi and nextjs using ghcr.io image references

**Step 4: Commit docker-compose changes**

```bash
git add docker-compose.prod.yml
git commit -m "feat: use pre-built images from GitHub Packages"
```

---

## Task 3: Add Version Variable to Environment Template

**Files:**
- Modify: `.env.production`

**Step 1: Read current .env.production**

Run: `head -20 .env.production`
Expected: See current environment variables

**Step 2: Add version variable at top of file**

Edit `.env.production`, add at the very top (before any other variables):

```bash
# ==========================================
# MiniBiblio Version
# ==========================================
# Change this to upgrade or rollback versions
# Format: 1.0.0 (without 'v' prefix) or 'latest' for newest release
MINIBIBLIO_VERSION=latest

```

**Step 3: Verify addition**

Run: `head -10 .env.production`
Expected: See MINIBIBLIO_VERSION=latest at the top

**Step 4: Commit environment template update**

```bash
git add .env.production
git commit -m "feat: add version control variable to environment template"
```

---

## Task 4: Update DEPLOYMENT.md Documentation

**Files:**
- Modify: `DEPLOYMENT.md`

**Step 1: Read current DEPLOYMENT.md structure**

Run: `head -50 DEPLOYMENT.md`
Expected: See current deployment documentation structure

**Step 2: Add version management section**

Edit `DEPLOYMENT.md`, add a new section after the installation instructions:

```markdown
## Version Management

### Checking Current Version

To see which version of MiniBiblio you're running:

1. Check your `.env` file:
   ```batch
   type .env | findstr MINIBIBLIO_VERSION
   ```

2. Or check the running containers:
   ```batch
   docker images | findstr minibiblio
   ```

### Updating to a New Version

When a new version is released:

1. **Edit your `.env` file** and update the version:
   ```bash
   MINIBIBLIO_VERSION=1.1.0
   ```

2. **Pull the new images**:
   ```batch
   docker-compose -f docker-compose.prod.yml pull
   ```

3. **Restart services**:
   ```batch
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Database migrations run automatically** when the FastAPI container starts.

### Rolling Back to a Previous Version

If you need to rollback:

1. **Edit `.env`** and change to the previous version:
   ```bash
   MINIBIBLIO_VERSION=1.0.0
   ```

2. **Pull and restart** (same commands as updating):
   ```batch
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Using Latest Version

To always use the newest release without manual updates:

```bash
MINIBIBLIO_VERSION=latest
```

Then run `docker-compose pull && docker-compose up -d` periodically to get updates.

### Available Versions

Check available versions at:
- GitHub Releases: https://github.com/helmecke/minibiblio/releases
- GitHub Packages: https://github.com/helmecke/minibiblio/pkgs/container/minibiblio-nextjs

### Troubleshooting Image Pulls

**Problem**: `Error response from daemon: pull access denied`

**Solution**: Ensure the GitHub Packages are set to public visibility.

**Problem**: `manifest unknown: manifest unknown`

**Solution**: The version doesn't exist. Check available versions in GitHub Packages.

**Problem**: Old version still running after update

**Solution**: Force recreation of containers:
```batch
docker-compose -f docker-compose.prod.yml up -d --force-recreate
```
```

**Step 3: Verify documentation addition**

Run: `grep -A5 "Version Management" DEPLOYMENT.md`
Expected: See the new version management section

**Step 4: Commit documentation update**

```bash
git add DEPLOYMENT.md
git commit -m "docs: add version management and update procedures"
```

---

## Task 5: Update README with Version Badge and Quick Start

**Files:**
- Modify: `README.md`

**Step 1: Read current README structure**

Run: `head -30 README.md`
Expected: See current README title and introduction

**Step 2: Add version badge near top**

Edit `README.md`, add badges section after the title (adjust based on current structure):

```markdown
# MiniBiblio

![GitHub release (latest by date)](https://img.shields.io/github/v/release/helmecke/minibiblio?label=version)
![Docker Pulls](https://img.shields.io/badge/docker-ghcr.io-blue)
![License](https://img.shields.io/github/license/helmecke/minibiblio)

A comprehensive library management system for small libraries.
```

**Step 3: Add quick start section**

Add or update a "Quick Start" section:

```markdown
## Quick Start

### Using Pre-built Images (Recommended)

1. **Download the deployment files**:
   ```bash
   wget https://raw.githubusercontent.com/helmecke/minibiblio/main/docker-compose.prod.yml
   wget https://raw.githubusercontent.com/helmecke/minibiblio/main/.env.production
   ```

2. **Configure environment**:
   ```bash
   cp .env.production .env
   # Edit .env with your credentials
   ```

3. **Start MiniBiblio**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Access the application**:
   - Web Interface: http://localhost:3000
   - Default credentials: admin / (see .env for ADMIN_PASSWORD)

### Building from Source

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed build instructions.
```

**Step 4: Verify README updates**

Run: `head -50 README.md | grep -E "(version|Quick Start)"`
Expected: See version badge and Quick Start section

**Step 5: Commit README update**

```bash
git add README.md
git commit -m "docs: add version badge and quick start guide"
```

---

## Task 6: Enhance install.bat with Version Information

**Files:**
- Modify: `install.bat`

**Step 1: Read current install.bat**

Run: `cat install.bat`
Expected: See current installation script logic

**Step 2: Add version information display**

Edit `install.bat`, add after the banner/header (around line 10-15):

```batch
echo.
echo ==========================================
echo MiniBiblio Installation
echo ==========================================
echo.
echo This installer will use pre-built Docker images from GitHub Packages.
echo Default version: latest (always uses newest release)
echo.
echo To use a specific version, edit MINIBIBLIO_VERSION in .env after installation.
echo Available versions: https://github.com/helmecke/minibiblio/releases
echo.
```

**Step 3: Add note after .env creation**

Find where `.env.production` is copied to `.env`, add after that section:

```batch
echo.
echo .env file created. Using default version (latest).
echo To pin to a specific version, edit MINIBIBLIO_VERSION in .env
echo Example: MINIBIBLIO_VERSION=1.0.0
echo.
```

**Step 4: Verify install.bat changes**

Run: `type install.bat | findstr MINIBIBLIO_VERSION`
Expected: See version-related messages

**Step 5: Commit install.bat enhancement**

```bash
git add install.bat
git commit -m "feat: add version information to installer"
```

---

## Task 7: Create update.bat Enhancement for Version Updates

**Files:**
- Modify: `update.bat`

**Step 1: Read current update.bat**

Run: `cat update.bat`
Expected: See current update script

**Step 2: Add version check and pull steps**

Edit `update.bat`, replace or enhance with:

```batch
@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo MiniBiblio Update Script
echo ==========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

REM Show current version
echo Current configuration:
type .env | findstr MINIBIBLIO_VERSION
echo.

REM Pull latest images
echo Pulling latest Docker images...
docker-compose -f docker-compose.prod.yml pull
if errorlevel 1 (
    echo ERROR: Failed to pull images
    pause
    exit /b 1
)

echo.
echo Stopping current containers...
docker-compose -f docker-compose.prod.yml down

echo.
echo Starting updated containers...
docker-compose -f docker-compose.prod.yml up -d
if errorlevel 1 (
    echo ERROR: Failed to start containers
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Update Complete!
echo ==========================================
echo.
echo Services are starting up...
echo Database migrations will run automatically.
echo.
echo Check status: docker-compose -f docker-compose.prod.yml ps
echo View logs: docker-compose -f docker-compose.prod.yml logs -f
echo.
pause
```

**Step 3: Verify update.bat changes**

Run: `type update.bat | findstr "version pull"`
Expected: See version checking and image pulling logic

**Step 4: Commit update.bat enhancement**

```bash
git add update.bat
git commit -m "feat: enhance update script with version awareness"
```

---

## Task 8: Verification and Testing Preparation

**Files:**
- Create: `docs/plans/verification-checklist.md`

**Step 1: Create verification checklist**

Create `docs/plans/verification-checklist.md`:

```markdown
# Docker GitHub Packages - Verification Checklist

## Pre-Release Verification

### 1. Workflow Syntax
- [ ] Workflow file has valid YAML syntax
- [ ] Trigger pattern matches semantic versions only
- [ ] Matrix includes both nextjs and fastapi
- [ ] Permissions include packages:write

### 2. Docker Compose Configuration
- [ ] Both services use ghcr.io image references
- [ ] Version variable ${MINIBIBLIO_VERSION:-latest} present
- [ ] Build sections completely removed
- [ ] All other configuration unchanged

### 3. Environment Template
- [ ] MINIBIBLIO_VERSION variable at top of .env.production
- [ ] Default value set to 'latest'
- [ ] Comments explain version format

### 4. Documentation
- [ ] DEPLOYMENT.md has version management section
- [ ] README.md has version badge
- [ ] README.md has quick start guide
- [ ] install.bat mentions version information
- [ ] update.bat handles version updates

## Test Release (v0.1.0)

### 1. Create Test Tag
```bash
git checkout main
git pull
git tag v0.1.0
git push origin v0.1.0
```

### 2. Monitor Workflow
- [ ] Workflow triggers automatically
- [ ] Both jobs (nextjs, fastapi) start in parallel
- [ ] Buildx setup succeeds
- [ ] Login to ghcr.io succeeds
- [ ] Both images build successfully
- [ ] Images tagged with 0.1.0 and latest
- [ ] Images pushed to ghcr.io

### 3. Verify Images Published
- [ ] Visit: https://github.com/helmecke?tab=packages
- [ ] See minibiblio-nextjs package
- [ ] See minibiblio-fastapi package
- [ ] Both show 0.1.0 and latest tags

### 4. Make Packages Public
- [ ] Navigate to package settings
- [ ] Change visibility to public
- [ ] Confirm packages accessible without auth

### 5. Test Pull Without Auth
```bash
docker pull ghcr.io/helmecke/minibiblio-nextjs:0.1.0
docker pull ghcr.io/helmecke/minibiblio-fastapi:0.1.0
```
- [ ] Both pulls succeed without login

### 6. Test Docker Compose Pull
```bash
# In a clean directory
export MINIBIBLIO_VERSION=0.1.0
docker-compose -f docker-compose.prod.yml pull
```
- [ ] Both services pull successfully

### 7. Test Version Update Flow
```bash
# Create v0.2.0 tag and push
# Edit .env: MINIBIBLIO_VERSION=0.2.0
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```
- [ ] New version pulls and starts
- [ ] Migrations run automatically
- [ ] Application accessible

## Success Criteria

- [x] All files committed to repository
- [ ] Test tag v0.1.0 triggers workflow
- [ ] Images published to ghcr.io within 10 minutes
- [ ] Packages set to public visibility
- [ ] Images pullable without authentication
- [ ] Version update workflow functional
- [ ] Documentation complete and accurate

## Notes

Record any issues or observations during verification:

---

```

**Step 2: Commit verification checklist**

```bash
git add docs/plans/verification-checklist.md
git commit -m "docs: add verification checklist for Docker publishing"
```

**Step 3: Review all commits**

Run: `git log --oneline -10`
Expected: See all 8 commits from this implementation

**Step 4: Push to remote (DO NOT CREATE TAG YET)**

```bash
git push origin main
```

Expected: All commits pushed successfully, workflow does NOT trigger (no tag yet)

---

## Post-Implementation Steps

### After Implementation Complete

1. **Review all changes**:
   ```bash
   git log --oneline -10
   git diff main~8..main
   ```

2. **DO NOT create tag yet** - wait for manual verification and approval

3. **When ready to test**, create test tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

4. **Monitor workflow**:
   - Go to: https://github.com/helmecke/minibiblio/actions
   - Watch "Build and Publish Docker Images" workflow
   - Verify both jobs complete successfully

5. **Make packages public**:
   - Navigate to: https://github.com/helmecke?tab=packages
   - For each package (minibiblio-nextjs, minibiblio-fastapi):
     - Click package → Package settings
     - Change visibility to "Public"
     - Confirm change

6. **Test pull without authentication**:
   ```bash
   docker pull ghcr.io/helmecke/minibiblio-nextjs:0.1.0
   docker pull ghcr.io/helmecke/minibiblio-fastapi:0.1.0
   ```

7. **Use verification checklist**: Follow `docs/plans/verification-checklist.md`

---

## Key Implementation Notes

### DRY Principle
- Matrix strategy eliminates duplicate workflow code
- Version variable in .env allows single source of truth
- Docker Compose references one variable for both services

### YAGNI Principle
- No multi-architecture builds (only amd64)
- No complex tagging strategies (just version + latest)
- No GitHub Releases automation (can add later)
- No build notifications (workflow UI sufficient)

### Testing Strategy
- Use v0.1.0 as test release before v1.0.0
- Verify workflow execution in GitHub Actions UI
- Test image pulls manually before documenting for users
- Validate version update flow with test versions

### Commit Strategy
- One commit per task (8 total)
- Clear commit messages following conventional commits
- Each commit is independently meaningful
- Easy to revert if needed

### Safety Considerations
- Workflow only triggers on semantic version tags (not every push)
- GITHUB_TOKEN used (no manual secret management)
- Default to 'latest' tag (users can pin if desired)
- Database migrations are idempotent (safe to re-run)
