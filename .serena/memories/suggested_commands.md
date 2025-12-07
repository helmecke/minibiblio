# Suggested Commands for MiniBiblio Development & Deployment

## Development Commands

### Python Environment
```bash
# Install Python dependencies
uv sync

# Add new Python dependency
uv add <package>

# Run Python development server
uv run uvicorn api.index:app --reload --port 8000

# Run database migrations
uv run alembic upgrade head

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Create admin user manually
uv run python api/scripts/create_admin.py
```

### Node.js Environment
```bash
# Install Node.js dependencies
npm install

# Run Next.js development server
npm run next-dev

# Run both servers concurrently
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint
```

### Database Management
```bash
# Start PostgreSQL (development)
docker compose up -d db

# Stop PostgreSQL
docker compose down

# View database logs
docker compose logs db

# Connect to database
docker exec -it minibiblio-db-1 psql -U postgres minibiblio

# Create database backup
docker exec minibiblio-db-1 pg_dump -U postgres minibiblio > backup.sql

# Restore database
docker exec -i minibiblio-db-1 psql -U postgres minibiblio < backup.sql
```

## Production Deployment Commands (Windows)

### Installation & Setup
```batch
# Install MiniBiblio (Windows)
install.bat

# Start MiniBiblio (Windows)
start.bat

# Stop MiniBiblio (Windows)
stop.bat

# View logs (Windows)
logs.bat

# Update MiniBiblio (Windows)
update.bat
```

### Docker Production Commands
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Stop production services
docker-compose -f docker-compose.prod.yml down

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker-compose -f docker-compose.prod.yml logs nextjs
docker-compose -f docker-compose.prod.yml logs fastapi
docker-compose -f docker-compose.prod.yml logs db

# Restart specific service
docker-compose -f docker-compose.prod.yml restart nextjs
docker-compose -f docker-compose.prod.yml restart fastapi
docker-compose -f docker-compose.prod.yml restart db
```

### Database Backup & Restore (Windows)
```batch
# Create database backup
scripts\backup.bat

# Restore database backup
scripts\restore.bat

# Setup automatic daily backups
scripts\setup-auto-backup.bat
```

### Database Backup & Restore (Cross-platform)
```bash
# Create timestamped backup
docker exec minibiblio-db-1 pg_dump -U postgres minibiblio > backups/minibiblio-backup-$(date +%Y%m%d-%H%M%S).sql

# Restore from backup
docker exec -i minibiblio-db-1 psql -U postgres minibiblio < backups/backup-file.sql

# List all backups
ls -la backups/

# Create backup directory if needed
mkdir -p backups
```

## Docker Management Commands

### Container Management
```bash
# List all containers
docker ps -a

# List running containers
docker ps

# View container logs
docker logs <container-name>

# Execute command in container
docker exec -it <container-name> /bin/bash

# Remove stopped containers
docker container prune

# View container resource usage
docker stats
```

### Image Management
```bash
# List all images
docker images

# Remove unused images
docker image prune

# Remove all images (force)
docker rmi -f $(docker images -q)

# Build specific image
docker build -f Dockerfile.nextjs -t minibiblio-nextjs .
docker build -f Dockerfile.fastapi -t minibiblio-fastapi .
```

### Volume Management
```bash
# List all volumes
docker volume ls

# Inspect volume
docker volume inspect <volume-name>

# Remove unused volumes
docker volume prune

# Backup volume
docker run --rm -v <volume-name>:/data -v $(pwd):/backup alpine tar czf /backup/volume-backup.tar.gz /data
```

### Network Management
```bash
# List all networks
docker network ls

# Inspect network
docker network inspect <network-name>

# Remove unused networks
docker network prune
```

## Troubleshooting Commands

### Health Checks
```bash
# Check service health
docker-compose -f docker-compose.prod.yml ps

# Test database connection
docker exec minibiblio-db-1 pg_isready -U postgres

# Test FastAPI health endpoint
curl http://localhost:8000/api/python/healthcheck

# Test Next.js application
curl http://localhost:3000
```

### Debugging
```bash
# View detailed logs with timestamps
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# View logs from last 5 minutes
docker-compose -f docker-compose.prod.yml logs --since=5m

# Follow logs for specific service
docker-compose -f docker-compose.prod.yml logs -f fastapi

# Check container resource usage
docker stats --no-stream

# Inspect container configuration
docker inspect minibiblio-nextjs
docker inspect minibiblio-fastapi
docker inspect minibiblio-db
```

### Common Issues
```bash
# Fix permission issues (Linux/Mac)
sudo chown -R $USER:$USER .

# Clean up Docker completely
docker system prune -a --volumes

# Rebuild from scratch
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Reset admin user
docker-compose -f docker-compose.prod.yml down -v
# Edit .env to change ADMIN_PASSWORD
docker-compose -f docker-compose.prod.yml up -d
```

## Testing Commands

### Backend Testing
```bash
# Run FastAPI tests (if implemented)
uv run pytest

# Test authentication endpoint
curl -X POST http://localhost:8000/api/python/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Test protected endpoint
curl -X GET http://localhost:8000/api/python/auth/me \
  -H "Authorization: Bearer <jwt-token>"
```

### Frontend Testing
```bash
# Run Next.js tests (if implemented)
npm test

# Run E2E tests (if implemented)
npm run test:e2e

# Build and test production build
npm run build
npm start
```

### Integration Testing
```bash
# Test full application
npm run dev
# Open http://localhost:3000
# Test login with admin/admin123
# Test catalog, patrons, circulation features
```

## Performance Monitoring

### Resource Usage
```bash
# Monitor Docker resource usage
docker stats

# Check disk usage
df -h
docker system df

# Monitor memory usage
free -h
docker stats --no-stream | grep minibiblio
```

### Application Performance
```bash
# Test API response time
time curl http://localhost:8000/api/python/healthcheck

# Test database query performance
docker exec minibiblio-db-1 psql -U postgres minibiblio -c "EXPLAIN ANALYZE SELECT * FROM patrons LIMIT 10;"

# Monitor application logs for errors
docker-compose -f docker-compose.prod.yml logs | grep -i error
```

## Security Commands

### Security Scanning
```bash
# Scan Docker images for vulnerabilities
docker scan minibiblio-nextjs
docker scan minibiblio-fastapi

# Check for exposed ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432
```

### Certificate Management (if HTTPS enabled)
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/private.key -out ssl/certificate.crt

# Check certificate expiry
openssl x509 -in ssl/certificate.crt -noout -dates
```

## Maintenance Commands

### Regular Maintenance
```bash
# Clean up Docker resources
docker system prune

# Update Docker images
docker-compose -f docker-compose.prod.yml pull

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Check logs for issues
docker-compose -f docker-compose.prod.yml logs --since=24h | grep -i error
```

### Backup Management
```bash
# List old backups
ls -la backups/ | head -20

# Remove backups older than 30 days
find backups/ -name "*.sql" -mtime +30 -delete

# Compress old backups
gzip backups/*.sql
```

### Log Management
```bash
# Rotate logs (if using log rotation)
docker-compose -f docker-compose.prod.yml logs --no-log-prefix > logs/minibiblio-$(date +%Y%m%d).log

# Clear old logs
docker-compose -f docker-compose.prod.yml logs --tail=0 > /dev/null
```

## Environment-Specific Commands

### Development Environment
```bash
# Start development services
npm run dev

# Run with hot reload
npm run next-dev &
uv run uvicorn api.index:app --reload &

# Test with local database
docker compose up -d db
npm run dev
```

### Production Environment
```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d --build

# Scale services (if needed)
docker-compose -f docker-compose.prod.yml up -d --scale nextjs=2

# Update production
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

### Windows-Specific Commands
```batch
# Open PowerShell as Administrator for Docker commands
# Run all batch files from Command Prompt or PowerShell

# Check Windows version
winver

# Check Docker Desktop status
docker --version
docker info

# Manage Windows services (if running as Windows service)
sc query docker
net start com.docker.service
```

## Git Commands (if using version control)

```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit"

# Add remote and push
git remote add origin <repository-url>
git push -u origin main

# Create development branch
git checkout -b feature/new-feature
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Merge to main
git checkout main
git merge feature/new-feature
git push origin main

# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Quick Reference Cheat Sheet

### Essential Commands
```bash
# Development
npm run dev                    # Start development
uv run uvicorn api.index:app --reload  # Start FastAPI dev

# Production (Windows)
start.bat                      # Start application
stop.bat                       # Stop application
logs.bat                       # View logs

# Docker
docker-compose -f docker-compose.prod.yml up -d    # Start production
docker-compose -f docker-compose.prod.yml down     # Stop production
docker-compose -f docker-compose.prod.yml logs -f   # View logs

# Database
uv run alembic upgrade head    # Run migrations
scripts/backup.bat             # Create backup
scripts/restore.bat            # Restore backup
```

### Default Credentials
```
Username: admin
Password: admin123
URL: http://localhost:3000
```

### Important Files
```
.env                    # Configuration (DO NOT COMMIT)
.env.production         # Configuration template
docker-compose.prod.yml # Production Docker config
DEPLOYMENT.md           # Deployment guide
install.bat             # Installation script
```