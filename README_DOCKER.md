# Learning Log - Docker Deployment Guide

Deploy Learning Log using Docker in production or development environments.

## 🚀 Quick Start

```bash
git clone <your-repo-url>
cd learning-log
cp .env.example .env
# Edit .env and change SECRET_KEY
./deploy.sh
```

Access at: http://localhost:5000

## 📋 Deployment Options

### PostgreSQL (Production)
```bash
docker-compose up -d
```

### SQLite (Development)
```bash
docker-compose -f docker-compose.sqlite.yml up -d
```

## ⚙️ Configuration

### Required Environment Variables

Edit `.env` file:
- `SECRET_KEY` - Flask secret key (**CHANGE THIS!**)
- `POSTGRES_PASSWORD` - Database password (PostgreSQL only)

Generate secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 📊 Management

### Basic Commands
```bash
docker-compose logs -f web        # View logs
docker-compose down               # Stop services
docker-compose restart            # Restart services
docker-compose up -d --build      # Update and restart
```

### Database Backup
```bash
# PostgreSQL
docker-compose exec db pg_dump -U postgres learning_log > backup.sql

# SQLite
cp instance/learning_log.db backup.db
```

## 🔧 Troubleshooting

```bash
docker-compose ps                    # Check status
docker-compose logs -f web          # Check logs
docker-compose down -v              # Reset everything
docker-compose up -d --build        # Rebuild and start
```

### Common Issues
- **Database connection failed**: Check `.env` configuration
- **Permission denied**: Run `chmod +x deploy.sh`
- **Port in use**: Change port to `"5001:5000"` in docker-compose.yml

## 🌐 Production Deployment

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
    }
}
```

### SSL Certificate
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🔒 Security Checklist

- [ ] Change SECRET_KEY and database passwords
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure firewall
- [ ] Set up database backups
- [ ] Monitor logs