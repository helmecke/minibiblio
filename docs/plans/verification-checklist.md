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

