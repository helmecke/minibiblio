# Docker Image Publishing to GitHub Packages - Design Plan

## Overview

Automated Docker image builds and publishing to GitHub Container Registry (ghcr.io) triggered by semantic version tags on the main branch.

## Goals

- **Self-contained deployment**: Users pull pre-built images instead of building locally
- **Version control**: Users can pin specific versions or use latest
- **Automated releases**: Tag-based workflow, no manual image builds
- **Fast iterations**: Layer caching for quick subsequent builds

## Design Decisions

### 1. Versioning Strategy

- **Format**: Semantic versioning with `v` prefix (e.g., `v1.0.0`, `v1.2.3`)
- **Trigger**: GitHub Actions workflow triggers on tags matching `v[0-9]+.[0-9]+.[0-9]+`
- **Image Tags**: 
  - Version tag: `ghcr.io/helmecke/minibiblio-{service}:1.0.0` (without 'v')
  - Latest tag: `ghcr.io/helmecke/minibiblio-{service}:latest`

### 2. Database Migrations

- **Automatic on startup**: FastAPI container runs migrations via `docker-entrypoint.sh`
- **Idempotent**: Safe to run multiple times (`alembic upgrade head`)
- **User experience**: Zero manual intervention - `docker-compose up -d` handles everything

### 3. Architecture Support

- **Platform**: `linux/amd64` only (primary target: Windows 11 users)
- **Future-proof**: Can add `linux/arm64` with 3-line change if needed
- **Build time**: ~5-7 minutes for both images in parallel

### 4. Version Management

- **User control**: `.env` variable `MINIBIBLIO_VERSION=1.0.0`
- **Docker Compose**: Uses `${MINIBIBLIO_VERSION:-latest}` for image references
- **Update workflow**: Edit `.env`, run `docker-compose pull && docker-compose up -d`

## Implementation Components

### GitHub Actions Workflow

**File**: `.github/workflows/docker-publish.yml`

**Trigger**:
```yaml
on:
  push:
    tags:
      - 'v[0-9]+.[0-9]+.[0-9]+'
```

**Job Structure**:
- Single job: `build-and-push`
- Matrix strategy for parallel builds (nextjs + fastapi)
- Runs on: `ubuntu-latest`
- Permissions: `contents: read`, `packages: write`

**Key Steps**:
1. Checkout repository
2. Extract version from tag (strip 'v' prefix)
3. Setup Docker Buildx
4. Login to ghcr.io (using `GITHUB_TOKEN`)
5. Build and push images (with caching)

**Matrix Configuration**:
```yaml
strategy:
  matrix:
    include:
      - image: nextjs
        dockerfile: Dockerfile.nextjs
        context: .
      - image: fastapi
        dockerfile: Dockerfile.fastapi
        context: .
```

**Build Optimization**:
- Cache type: GitHub Actions cache (`type=gha`)
- Cache mode: `max` (cache all layers)
- Expected speedup: 50-70% faster on subsequent builds

### Docker Compose Changes

**File**: `docker-compose.prod.yml`

**Before** (build locally):
```yaml
fastapi:
  build:
    context: .
    dockerfile: Dockerfile.fastapi
```

**After** (pull from registry):
```yaml
fastapi:
  image: ghcr.io/helmecke/minibiblio-fastapi:${MINIBIBLIO_VERSION:-latest}
```

**Changes**:
- Remove `build:` sections from both services
- Add `image:` references with environment variable
- Keep all other configuration (environment, depends_on, networks, etc.)

### Environment Configuration

**File**: `.env.production` (template)

**New Variables**:
```bash
# MiniBiblio Version (change this to update)
MINIBIBLIO_VERSION=1.0.0
```

**User Workflow**:
1. Copy `.env.production` to `.env`
2. Edit credentials and configuration
3. `MINIBIBLIO_VERSION` controls which release to use
4. Default to `latest` if not specified

### Image Naming Convention

**Registry**: GitHub Container Registry (ghcr.io)
**Owner**: helmecke
**Images**:
- `ghcr.io/helmecke/minibiblio-nextjs:1.0.0`
- `ghcr.io/helmecke/minibiblio-nextjs:latest`
- `ghcr.io/helmecke/minibiblio-fastapi:1.0.0`
- `ghcr.io/helmecke/minibiblio-fastapi:latest`

## Release Process

### Developer Steps

1. **Prepare release**:
   - Ensure all changes committed on `main`
   - Update version in relevant files
   - Test locally

2. **Create tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **GitHub Actions automatically**:
   - Builds both Docker images
   - Tags with version + latest
   - Pushes to ghcr.io
   - Takes ~5-7 minutes

4. **Update template**:
   - Edit `.env.production` with new `MINIBIBLIO_VERSION`
   - Commit and push

5. **Make package public** (one-time):
   - Go to GitHub package settings
   - Change visibility to public
   - Users can pull without authentication

### User Update Workflow

**Initial Install**:
```bash
install.bat  # Copies .env.production, prompts for credentials
# Docker Compose pulls images automatically
```

**Update to New Version**:
1. Edit `.env` file: `MINIBIBLIO_VERSION=1.1.0`
2. Run:
   ```bash
   docker-compose -f docker-compose.prod.yml pull
   docker-compose -f docker-compose.prod.yml up -d
   ```
3. Migrations run automatically on startup

**Rollback**:
1. Edit `.env` file: `MINIBIBLIO_VERSION=1.0.0`
2. Run same pull/up commands
3. Database migrations are forward-compatible

## Documentation Updates

### DEPLOYMENT.md

**New Sections**:
- Version management and update process
- How to check current version
- Rollback procedures
- Troubleshooting image pulls

### README.md

**Additions**:
- Badge showing latest version from ghcr.io
- Link to releases page
- Quick start with pre-built images

### install.bat

**Potential Enhancements**:
- Prompt user for version or default to latest stable
- Show available versions from ghcr.io
- Validate version format

## Technical Details

### Build Caching Strategy

**GitHub Actions Cache**:
- Cache key: Based on Dockerfile + dependencies
- Storage: Automatic GitHub Actions cache
- Retention: 7 days of inactivity
- Size: ~500MB-1GB per image

**Performance**:
- First build: ~7-10 minutes (downloads all dependencies)
- Cached builds: ~2-4 minutes (reuses layers)
- Parallel builds: Both images build simultaneously

### Security & Permissions

**Workflow Permissions**:
- `contents: read` - Checkout code
- `packages: write` - Push to ghcr.io
- Uses `GITHUB_TOKEN` (automatic, no secrets needed)

**Image Visibility**:
- Default: Private (requires authentication)
- Recommended: Public (easier user experience)
- Setting: One-time change in GitHub UI

### Database Migration Safety

**Automatic Migration Benefits**:
- No user intervention required
- Idempotent (safe to run multiple times)
- Fails fast if migration errors
- Logs migration output for debugging

**Handled by docker-entrypoint.sh**:
1. Wait for PostgreSQL health
2. Run `alembic upgrade head`
3. Create default admin user
4. Start FastAPI server

## Files to Create/Modify

### New Files
- `.github/workflows/docker-publish.yml` - GitHub Actions workflow

### Modified Files
- `docker-compose.prod.yml` - Switch from build to image references
- `.env.production` - Add MINIBIBLIO_VERSION variable
- `DEPLOYMENT.md` - Document version management
- `README.md` - Add version badge and quick start

### Optional Enhancements
- `install.bat` - Version selection prompt
- `update.bat` - Automated version update script

## Future Considerations

### Multi-architecture Support

**Currently**: `linux/amd64` only
**To add arm64**: Add to platforms in workflow
```yaml
platforms: linux/amd64,linux/arm64
```
**Impact**: Doubles build time (~12-15 min)

### Additional Image Tags

**Possible additions**:
- Major version tags: `1`, `1.2` (auto-update to latest patch)
- SHA tags: `sha-abc123` (exact commit reference)
- Branch tags: `main`, `develop` (latest commit on branch)

**Current approach**: Keep it simple with version + latest only

### Build Notifications

**Potential enhancements**:
- Slack/Discord notifications on build success/failure
- GitHub Releases auto-creation with changelog
- Docker Hub mirroring for wider distribution

## Success Criteria

1. ✅ Push tag `v1.0.0` triggers automated build
2. ✅ Images published to ghcr.io within 10 minutes
3. ✅ Users can pull images without building locally
4. ✅ Version updates work with zero downtime
5. ✅ Database migrations run automatically on startup
6. ✅ Rollback possible by changing environment variable

## Rollout Plan

1. **Create workflow** - Test with `v0.1.0` tag
2. **Verify images** - Pull and test locally
3. **Update compose** - Switch to image references
4. **Test update flow** - Simulate version upgrade
5. **Document process** - Update DEPLOYMENT.md
6. **Make public** - Change package visibility
7. **Announce** - Update README with new workflow