@echo off
echo ========================================
echo MiniBiblio Logs
echo ========================================
echo:
echo Press Ctrl+C to stop viewing logs
echo:

docker-compose -f docker-compose.prod.yml logs -f
