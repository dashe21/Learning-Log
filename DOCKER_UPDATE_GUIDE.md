# 🐳 Docker Update Guide

Simple guide to update your Learning Log deployment.

## 🚀 Quick Update

```bash
./update-docker.sh
```

## Manual Update

```bash
docker compose build --no-cache web
docker compose up -d
```

## 🔄 Update Types

### Code Changes
```bash
docker compose down
docker compose build --no-cache web
docker compose up -d
```

### Fresh Start
```bash
docker compose down -v
docker compose up -d --build
```

## 💾 Backup Database

### PostgreSQL
```bash
docker compose exec db pg_dump -U postgres learning_log > backup.sql
```

### SQLite
```bash
cp instance/learning_log.db backup.db
```

## 🔍 Verify Update

```bash
docker compose ps                    # Check status
docker compose logs -f web          # Check logs
./test-deployment.sh                # Run tests
```

## 🐛 Troubleshooting

### Common Issues
- **Port in use**: Change port in docker-compose.yml to `"5001:5000"`
- **Build cache**: Run `docker builder prune -a`
- **Permissions**: Run `sudo chown -R $USER:$USER instance/`

### Rollback
```bash
docker compose down
git checkout HEAD~1
docker compose up -d --build
```

---

**Remember**: Always backup before updating! 💾