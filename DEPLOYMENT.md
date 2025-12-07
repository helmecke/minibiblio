# MiniBiblio - Windows Deployment Guide

## Overview

This guide explains how to deploy MiniBiblio on a Windows 11 laptop using Docker. The deployment includes:
- ✅ Local username/password authentication
- ✅ Persistent database storage
- ✅ Easy backup and restore
- ✅ One-command startup and management
- ✅ Optional Google OAuth

## Prerequisites

### Required Software
1. **Docker Desktop for Windows** - [Download here](https://www.docker.com/products/docker-desktop/)
   - Minimum: Windows 11 with WSL2 enabled
   - Ensure Docker is running before installation

### System Requirements
- **OS**: Windows 11
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 5GB free space
- **Internet**: Required for initial setup and Docker image downloads

## Installation Steps

### 1. Install Docker Desktop
```
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Follow the installation wizard
4. Restart your computer if prompted
5. Launch Docker Desktop
6. Wait for Docker to start (icon in system tray will turn green)
```

### 2. Prepare MiniBiblio

**Option A: If you have the source code**
```
1. Extract or clone MiniBiblio to a folder (e.g., C:\MiniBiblio)
2. Open that folder
```

**Option B: If using git**
```bash
git clone <repository-url> C:\MiniBiblio
cd C:\MiniBiblio
```

### 3. Run Installation Script

1. Double-click `install.bat` in the MiniBiblio folder
2. The script will check Docker and create a `.env` configuration file
3. Notepad will open with the `.env` file

### 4. Configure Environment Variables

In the `.env` file that opens, update these **required** values:

```env
# 1. Strong database password (use a password manager)
POSTGRES_PASSWORD=YourStrongPasswordHere123!

# 2. JWT Secret (generate at https://generate-secret.vercel.app/32)
JWT_SECRET=your_generated_jwt_secret_here

# 3. Auth Secret (generate at https://generate-secret.vercel.app/32) 
AUTH_SECRET=your_generated_auth_secret_here

# 4. Change default admin password
ADMIN_PASSWORD=ChangeThisPassword123!
```

**Important Security Notes:**
- Never use default passwords in production
- Generate random secrets using the provided URL
- Keep the `.env` file secure and backed up
- Never commit `.env` to version control

4. Save and close Notepad
5. Press `Y` to confirm configuration
6. Wait 5-10 minutes for Docker images to build

### 5. Start MiniBiblio

1. Double-click `start.bat`
2. Wait 30-60 seconds for services to initialize
3. Open your web browser to: `http://localhost:3000`

### 6. First Login

```
Username: admin
Password: admin123  (or what you set in ADMIN_PASSWORD)
```

**⚠️ CRITICAL: Change the admin password immediately!**

Go to Settings or User Profile and update your password.

## Daily Usage

### Starting MiniBiblio
```
Double-click: start.bat
Wait: 30-60 seconds
Open: http://localhost:3000
```

### Stopping MiniBiblio
```
Double-click: stop.bat
```

### Viewing Logs (Troubleshooting)
```
Double-click: logs.bat
Press Ctrl+C to stop viewing
```

### Updating MiniBiblio
```
Double-click: update.bat
```

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

## Database Backup & Restore

### Manual Backup

**Create a backup:**
```
1. Navigate to the 'scripts' folder
2. Double-click: backup.bat
3. Backup will be saved to: backups\minibiblio-backup-YYYYMMDD-HHMMSS.sql
```

**Restore from backup:**
```
1. Navigate to the 'scripts' folder
2. Double-click: restore.bat
3. Choose backup file from the list
4. Type YES to confirm
5. Wait for restore to complete
```

### Automatic Daily Backups

**Setup automatic backups at 2:00 AM daily:**
```
1. Right-click: scripts\setup-auto-backup.bat
2. Select "Run as administrator"
3. Confirm setup
```

**To disable automatic backups:**
```
Open Command Prompt as Administrator
Run: schtasks /delete /tn "MiniBiblio Daily Backup" /f
```

## File Structure

```
MiniBiblio/
├── install.bat                 # Installation script
├── start.bat                   # Start application
├── stop.bat                    # Stop application
├── logs.bat                    # View logs
├── update.bat                  # Update application
├── .env                        # Configuration (DO NOT COMMIT!)
├── .env.production             # Configuration template
├── docker-compose.prod.yml     # Docker services definition
├── Dockerfile.nextjs           # Next.js container
├── Dockerfile.fastapi          # FastAPI container
├── docker-entrypoint.sh        # FastAPI startup script
├── backups/                    # Database backups (auto-created)
│   └── minibiblio-backup-*.sql
├── scripts/
│   ├── backup.bat              # Create backup
│   ├── restore.bat             # Restore backup
│   └── setup-auto-backup.bat   # Schedule automatic backups
└── ...
```

## Troubleshooting

### Problem: Docker is not running
**Solution:**
```
1. Open Docker Desktop
2. Wait for it to fully start
3. Try running start.bat again
```

### Problem: Port 3000 is already in use
**Solution:**
```
1. Stop other applications using port 3000
2. Or edit docker-compose.prod.yml and change "3000:3000" to "8080:3000"
3. Access at http://localhost:8080 instead
```

### Problem: Cannot connect to database
**Solution:**
```
1. Run: stop.bat
2. Wait 10 seconds
3. Run: start.bat
4. Wait 60 seconds
5. Check logs: logs.bat
```

### Problem: Forgot admin password
**Solution:**
```
1. Stop MiniBiblio: stop.bat
2. Edit .env file
3. Change ADMIN_PASSWORD=NewPassword123
4. Run: docker-compose -f docker-compose.prod.yml down -v
5. Start again: start.bat
6. This recreates admin user with new password
```

### Problem: Application won't start
**Solution:**
```
1. Check Docker Desktop is running
2. Run: logs.bat
3. Look for error messages
4. Common fixes:
   - Restart Docker Desktop
   - Run: docker-compose -f docker-compose.prod.yml down
   - Run: start.bat
```

### View detailed logs:
```
# All services
docker-compose -f docker-compose.prod.yml logs

# Specific service
docker-compose -f docker-compose.prod.yml logs fastapi
docker-compose -f docker-compose.prod.yml logs nextjs
docker-compose -f docker-compose.prod.yml logs db
```

## Data Persistence

Your library data is stored in Docker volumes that persist between restarts:
- **Database**: `minibiblio_postgres_data`
- **Location**: Managed by Docker Desktop

### View Docker volumes:
```
docker volume ls
```

### Complete data reset (⚠️ DELETES ALL DATA):
```
docker-compose -f docker-compose.prod.yml down -v
```

## Security Best Practices

1. **Change default passwords immediately**
   - Admin password
   - Database password

2. **Use strong secrets**
   - Generate JWT_SECRET and AUTH_SECRET using secure random generators
   - Never reuse secrets across environments

3. **Keep backups secure**
   - Store backups in a secure location
   - Encrypt sensitive backups
   - Test restore procedures regularly

4. **Regular updates**
   - Run update.bat monthly to get security patches
   - Review changelog before updating

5. **Network security**
   - Default config only allows localhost access
   - To allow network access, configure NEXTAUTH_URL in .env
   - Consider using a reverse proxy (Caddy, Nginx) for HTTPS

## Advanced Configuration

### Enable Google OAuth

1. Get Google OAuth credentials:
   - Visit: https://console.cloud.google.com/apis/credentials
   - Create OAuth 2.0 Client ID
   - Add authorized redirect: http://localhost:3000/api/auth/callback/google

2. Update `.env`:
```env
ENABLE_GOOGLE_AUTH=true
AUTH_GOOGLE_ID=your_google_client_id
AUTH_GOOGLE_SECRET=your_google_client_secret
```

3. Restart: `stop.bat` then `start.bat`

### Change Default Port

Edit `docker-compose.prod.yml`:
```yaml
nextjs:
  ports:
    - "8080:3000"  # Change 8080 to your preferred port
```

### Access from Other Devices on Network

1. Find your Windows IP address:
   ```
   ipconfig
   ```

2. Update `.env`:
   ```env
   NEXTAUTH_URL=http://YOUR_IP_ADDRESS:3000
   ```

3. Restart MiniBiblio

4. Access from other devices: `http://YOUR_IP_ADDRESS:3000`

## Uninstallation

To completely remove MiniBiblio:

1. Stop services:
   ```
   stop.bat
   ```

2. Remove containers and volumes:
   ```
   docker-compose -f docker-compose.prod.yml down -v
   ```

3. Remove Docker images:
   ```
   docker image rm minibiblio-nextjs minibiblio-fastapi
   ```

4. Delete MiniBiblio folder

5. (Optional) Remove Docker Desktop if no longer needed

## Support & Resources

- **Documentation**: See README.md
- **Source Code**: Check repository
- **Docker Docs**: https://docs.docker.com/
- **Next.js Docs**: https://nextjs.org/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/

## Maintenance Schedule

### Daily
- Automatic backups run at 2 AM (if configured)

### Weekly
- Review logs for errors: `logs.bat`
- Check disk space usage

### Monthly
- Run `update.bat` to get latest updates
- Test backup restore procedure
- Review user access and permissions

### Quarterly
- Review and update passwords
- Audit database size
- Clean up old backups (keep last 3 months)

## Performance Tips

1. **Allocate more resources to Docker**
   - Open Docker Desktop → Settings → Resources
   - Increase CPUs: 2-4 cores
   - Increase Memory: 4-8 GB

2. **Regular maintenance**
   - Prune unused Docker images: `docker system prune`
   - Keep only recent backups

3. **Monitor performance**
   - Use `logs.bat` to check for slow queries
   - Watch Docker Desktop resource usage

---

**Congratulations!** MiniBiblio is now deployed on your Windows 11 laptop. Happy cataloging! 📚
